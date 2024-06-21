import logging
import time
from datetime import datetime, timedelta, timezone


class TimeSynchronizer:
    def __init__(self):
        self.server_time_reference = None
        self.local_time_reference = None
        self.timezone_offset = timedelta(seconds=self._get_local_timezone_offset())

    @staticmethod
    def _get_local_timezone_offset():
        """
        Obtiene el desplazamiento de la zona horaria local en segundos.

        :return: Desplazamiento de la zona horaria local en segundos.
        """
        local_time = datetime.now()
        utc_time = datetime.utcnow()
        offset = (local_time - utc_time).total_seconds()
        return offset

    def synchronize(self, server_time):
        """
        Sincroniza el tiempo local con el tiempo del servidor.

        :param server_time: Tiempo del servidor en segundos (puede ser un timestamp).
        """

        self.server_time_reference = server_time
        self.local_time_reference = time.time()

    def get_synced_time(self):
        """
        Obtiene el tiempo sincronizado basado en el tiempo actual del sistema.

        :return: Tiempo sincronizado en segundos.
        """
        if self.server_time_reference is None or self.local_time_reference is None:
            raise ValueError("El tiempo no ha sido sincronizado aún.")

        # Calcula la diferencia de tiempo desde la última sincronización
        elapsed_time = time.time() - self.local_time_reference
        # Calcula el tiempo sincronizado
        synced_time = self.server_time_reference + elapsed_time
        return synced_time

    def get_synced_datetime(self):
        """
        Convierte el tiempo sincronizado a un objeto datetime ajustado a la zona horaria local.

        :return: Tiempo sincronizado como un objeto datetime.
        """
        synced_time_seconds = self.get_synced_time()
        # Redondear los segundos
        rounded_time_seconds = round(synced_time_seconds)
        # Convertir a datetime en UTC
        synced_datetime_utc = datetime.fromtimestamp(rounded_time_seconds, tz=timezone.utc)
        # Ajustar el tiempo sincronizado a la zona horaria local
        synced_datetime_local = synced_datetime_utc + self.timezone_offset
        return synced_datetime_local

    def update_sync(self, new_server_time):
        """
        Actualiza la sincronización con un nuevo tiempo del servidor.

        :param new_server_time: Nuevo tiempo del servidor en segundos.
        """
        self.synchronize(new_server_time)
