from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFound
from app.db.models import Account
from app.repositories.account_repository import AccountRepository
from app.dto.input.account_input import AccountCreateDTO, AccountUpdateDTO
from app.dto.output.account_output import AccountOutputDTO


class AccountService:
    def __init__(self, session: AsyncSession):
        self._repo = AccountRepository(session=session)

    async def create(self, user_id: UUID, data: AccountCreateDTO) -> AccountOutputDTO:
        account = Account(
            user_id=user_id,
            name=data.name,
            type=data.type,
            balance=0,
            currency=data.currency,
        )
        account = await self._repo.add(account)
        return AccountOutputDTO.model_validate(account)

    async def list_accounts(self, user_id: UUID) -> list[AccountOutputDTO]:
        accounts = await self._repo.list_by_user(user_id)
        return [AccountOutputDTO.model_validate(a) for a in accounts]

    async def get(self, uuid: UUID, user_id: UUID) -> AccountOutputDTO:
        account = await self._repo.get(uuid)
        if account.user_id != user_id:
            raise EntityNotFound("Account", str(uuid))
        return AccountOutputDTO.model_validate(account)

    async def update(self, uuid: UUID, user_id: UUID, data: AccountUpdateDTO) -> AccountOutputDTO:
        account = await self._repo.get(uuid)
        if account.user_id != user_id:
            raise EntityNotFound("Account", str(uuid))
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return AccountOutputDTO.model_validate(account)
        account = await self._repo.update(uuid, update_data)
        return AccountOutputDTO.model_validate(account)

    async def delete(self, uuid: UUID, user_id: UUID) -> None:
        account = await self._repo.get(uuid)
        if account.user_id != user_id:
            raise EntityNotFound("Account", str(uuid))
        await self._repo.delete(uuid)
