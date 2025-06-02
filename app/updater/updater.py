
import asyncio
from loguru import logger

from aiomonobnk.types import InvoiceStatus
from aiomonobnk.enums import TransactionStatus

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import AssignStatus
from app.model import ProductAssign, Payment
from app.database import get_async_session
from app.mono import mono_client

from config import get_settings


class Updater:
    def __init__(self):
        self.log = logger.bind(classname=self.__class__.__name__)

        self.tasks = [self.check_assigns]
        self.__tasks = []

        self.check_assigns_semaphore = asyncio.Semaphore(get_settings().updater.check_payment_status_concurrency)
        self.delay = get_settings().updater.task_delay_seconds

    async def update_assign_status(self, assign: ProductAssign, payment: Payment, session: AsyncSession):
        async with self.check_assigns_semaphore:
            invoice: InvoiceStatus = await mono_client.invoice_status(payment.external_id)

        if invoice.status in [TransactionStatus.CREATED, TransactionStatus.PROCESSING, TransactionStatus.HOLD]:
            return None

        new_status = {
            TransactionStatus.SUCCESS: AssignStatus.success,
            TransactionStatus.FAILURE: AssignStatus.cancelled,
            TransactionStatus.REVERSER: AssignStatus.cancelled,
            TransactionStatus.EXPIRED: AssignStatus.expired,
        }.get(invoice.status)

        if new_status is None:
            self.log.warning(f"Unknown status -> {invoice.status}")
            return

        elif new_status in [AssignStatus.expired, AssignStatus.cancelled]:
            pass

        await session.execute(
            update(ProductAssign)
            .where(ProductAssign.id == assign.id)
            .values(status=new_status)
            .execution_options(synchronize_session="fetch")
        )

    async def check_assigns(self):
        async with get_async_session() as session:
            assigns = (await session.execute(
                select(ProductAssign).where(ProductAssign.status.in_([AssignStatus.pending]))
            )).scalars().all()

            if not len(assigns):
                return

            payments = (await session.execute(
                select(Payment).where(Payment.id.in_(map(lambda x: x.payment_id, assigns)))
            )).scalars().all()

            payments_dict = {
                payment.id: payment
                for payment in payments
            }

            await asyncio.gather(*[
                self.update_assign_status(assign, payments_dict[assign.payment_id], session)
                for assign in assigns
            ])
            await session.commit()

    async def task_wrapper(self, func):
        while True:
            try:
                await func()

            except Exception as err:
                self.log.error(f"Occurred error with {func.__name__} -> {err}")
                self.log.exception(err)

            await asyncio.sleep(self.delay)

    async def start(self):
        self.log.info(f"Starting updater tasks")

        for task in self.tasks:
            self.tasks.append(asyncio.create_task(self.task_wrapper(task)))
            self.log.info(f"Started task -> {task.__name__}")
