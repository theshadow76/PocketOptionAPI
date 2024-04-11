import time
from datetime import datetime, timedelta

# https://docs.python.org/3/library/datetime.html If optional argument tz is None or not specified, the timestamp is
# converted to the platform's local date and time, and the returned datetime object is naive. time.mktime(
# dt.timetuple())


from datetime import datetime, timedelta
import time


def date_to_timestamp(date):
    """Convierte un objeto datetime a timestamp."""
    return int(date.timestamp())


def get_expiration_time(timestamp, duration):
    """
    Calcula el tiempo de expiración más cercano basado en un timestamp dado y una duración.
    El tiempo de expiración siempre terminará en el segundo:30 del minuto.

    :param timestamp: El timestamp inicial para el cálculo.
    :param duration: La duración deseada en minutos.
    """
    # Convertir el timestamp dado a un objeto datetime
    now_date = datetime.fromtimestamp(timestamp)

    # Ajustar los segundos a: 30 si no lo están ya, de lo contrario, pasar al siguiente: 30
    if now_date.second < 30:
        exp_date = now_date.replace(second=30, microsecond=0)
    else:
        exp_date = (now_date + timedelta(minutes=1)).replace(second=30, microsecond=0)

    # Calcular el tiempo de expiración teniendo en cuenta la duración
    if duration > 1:
        # Si la duración es más de un minuto, calcular el tiempo final agregando la duración
        # menos un minuto, ya que ya hemos ajustado para terminar en: 30 segundos.
        exp_date += timedelta(minutes=duration - 1)

    # Sumar dos horas al tiempo de expiración
    exp_date += timedelta(hours=2)
    # Convertir el tiempo de expiración a timestamp
    expiration_timestamp = date_to_timestamp(exp_date)

    return expiration_timestamp


def get_remaning_time(timestamp):
    now_date = datetime.fromtimestamp(timestamp)
    exp_date = now_date.replace(second=0, microsecond=0)
    if (int(date_to_timestamp(exp_date+timedelta(minutes=1)))-timestamp) > 30:
        exp_date = exp_date+timedelta(minutes=1)

    else:
        exp_date = exp_date+timedelta(minutes=2)
    exp = []
    for _ in range(5):
        exp.append(date_to_timestamp(exp_date))
        exp_date = exp_date+timedelta(minutes=1)
    idx = 11
    index = 0
    now_date = datetime.fromtimestamp(timestamp)
    exp_date = now_date.replace(second=0, microsecond=0)
    while index < idx:
        if int(exp_date.strftime("%M")) % 15 == 0 and (int(date_to_timestamp(exp_date))-int(timestamp)) > 60*5:
            exp.append(date_to_timestamp(exp_date))
            index = index+1
        exp_date = exp_date+timedelta(minutes=1)

    remaning = []

    for idx, t in enumerate(exp):
        if idx >= 5:
            dr = 15*(idx-4)
        else:
            dr = idx+1
        remaning.append((dr, int(t)-int(time.time())))

    return remaning