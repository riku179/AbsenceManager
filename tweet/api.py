from django.core.exceptions import ObjectDoesNotExist

from .tasks import update_attendance, reply_attendance

def api_update_attendance(user_id, attendances, today, api_ctrl):
    try:
        update_attendance.delay(user_id=user_id, attendances=attendance, today=today)
    except AttributeError:
        log.error('user:{user_id} failed update attendance. Option is disabled or pattern is too long.'
                  .format(user_id=msg['user']['id']))
    except ObjectDoesNotExist:
        log.error('user:{user_id} does not exist in DB.')
    except Exception as err:
            log.error("Unknown error occurred: {e}".format(e=err))
    else:
        reply_attendance.delay(user_id=msg['user']['id'], attendances=attendances, api_ctrl=api_ctrl)
