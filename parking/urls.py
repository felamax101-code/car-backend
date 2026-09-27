from django.urls import path

from .views import (
    GateListCreateView,
    ParkingLotListCreateView,
    ParkingSlotDetailView,
    ParkingSlotListCreateView,
    SlotAvailabilityView,
    SlotGridView,
    TariffDetailView,
    TariffListCreateView,
)

urlpatterns = [
    # Availability / display — read-only, any authenticated role
    path("lots/<int:lot_id>/availability/", SlotAvailabilityView.as_view(), name="slot-availability"),
    path("lots/<int:lot_id>/slots/", SlotGridView.as_view(), name="slot-grid"),

    # Admin configuration
    path("lots/", ParkingLotListCreateView.as_view(), name="lot-list-create"),
    path("slots/", ParkingSlotListCreateView.as_view(), name="slot-list-create"),
    path("slots/<int:pk>/", ParkingSlotDetailView.as_view(), name="slot-detail"),
    path("gates/", GateListCreateView.as_view(), name="gate-list-create"),
    path("tariffs/", TariffListCreateView.as_view(), name="tariff-list-create"),
    path("tariffs/<int:pk>/", TariffDetailView.as_view(), name="tariff-detail"),
]