from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from groq import AsyncGroq
from app.core.config import settings
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.account_repository import AccountRepository

AI_DISABLED_MESSAGE = "AI insights are disabled. Set GROQ_API_KEY to enable them."


class AiService:
    def __init__(self, session: AsyncSession):
        self._transaction_repo = TransactionRepository(session=session)
        self._account_repo = AccountRepository(session=session)
        self._client = AsyncGroq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

    async def analyze_spending(self, user_id: UUID) -> str:
        if not self._client:
            return AI_DISABLED_MESSAGE

        accounts = await self._account_repo.list_by_user(user_id)
        if not accounts:
            return "No accounts found. Add an account and transactions to get AI insights."

        all_transactions = []
        for account in accounts:
            transactions = await self._transaction_repo.list_by_account(account.uuid, limit=50)
            all_transactions.extend(transactions)

        if not all_transactions:
            return "No transactions found yet. Add some transactions to get personalized insights."

        summary_lines = []
        for t in all_transactions[:30]:
            category = t.category.name if t.category else "Uncategorized"
            summary_lines.append(f"{t.type.value}: {t.amount} UAH — {category} ({t.date})")

        transactions_text = "\n".join(summary_lines)

        prompt = f"""Проаналізуй ці особисті фінансові транзакції та дай 3 практичні поради українською мовою:
{transactions_text}

Відповідай українською. Будь конкретним, дружнім та корисним. Зосередься на патернах витрат та порадах щодо заощаджень."""

        response = await self._client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def chat(self, user_id: UUID, message: str) -> str:
        if not self._client:
            return AI_DISABLED_MESSAGE

        accounts = await self._account_repo.list_by_user(user_id)
        total_balance = sum(float(a.balance) for a in accounts)

        system_prompt = f"""Ти персональний фінансовий асистент. Завжди відповідай українською мовою.
Користувач має {len(accounts)} рахунок(и) із загальним балансом {total_balance:.2f} грн.
Допомагай з бюджетуванням, заощадженнями та фінансовими рішеннями. Будь конкретним та практичним."""

        response = await self._client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ]
        )
        return response.choices[0].message.content
