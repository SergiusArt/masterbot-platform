"""Service registry for managing connected services."""

from typing import Dict, List, Optional

from sqlalchemy import select

from services.base import BaseServiceClient
from shared.database.connection import async_session_maker
from shared.database.models import Service


class ServiceRegistry:
    """Registry for managing microservices."""

    def __init__(self):
        self._clients: Dict[str, BaseServiceClient] = {}

    async def get_active_services(self) -> List[Service]:
        """Get list of active services from database.

        Returns:
            List of active services
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(Service)
                .where(Service.is_active == True)
                .order_by(Service.menu_order)
            )
            return list(result.scalars().all())

    async def get_service(self, name: str) -> Optional[Service]:
        """Get service by name.

        Args:
            name: Service name

        Returns:
            Service or None
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(Service).where(Service.name == name)
            )
            return result.scalar_one_or_none()

    def get_client(self, service: Service) -> BaseServiceClient:
        """Get or create client for service.

        Args:
            service: Service model

        Returns:
            Service client
        """
        if service.name not in self._clients:
            self._clients[service.name] = BaseServiceClient(service.base_url)
        return self._clients[service.name]

    async def check_all_services_health(self) -> Dict[str, bool]:
        """Check health of all active services.

        Returns:
            Dictionary mapping service name to health status
        """
        services = await self.get_active_services()
        results = {}

        for service in services:
            client = self.get_client(service)
            results[service.name] = await client.health_check()

        return results

    async def register_service(
        self,
        name: str,
        display_name: str,
        base_url: str,
        description: Optional[str] = None,
        menu_icon: str = "📦",
        menu_order: int = 100,
    ) -> Service:
        """Register a new service.

        Args:
            name: Service unique name
            display_name: Display name for menus
            base_url: Service base URL
            description: Service description
            menu_icon: Menu icon emoji
            menu_order: Menu order number

        Returns:
            Created service
        """
        async with async_session_maker() as session:
            service = Service(
                name=name,
                display_name=display_name,
                base_url=base_url,
                description=description,
                menu_icon=menu_icon,
                menu_order=menu_order,
            )
            session.add(service)
            await session.commit()
            await session.refresh(service)
            return service


# Global registry instance
service_registry = ServiceRegistry()
