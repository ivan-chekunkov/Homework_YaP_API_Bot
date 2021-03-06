RETRY_TIME = 600

method_upload_const = 'path'

format_log = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

HOMEWORK_STATUSES = {
    'approved': ('Работа проверена: ревьюеру всё понравилось. Ура!',
                 'Поздравляю, работа выполнена успешно.',
                 'Супер! Ты справился и теперь можешь отдыхать!',
                 '\U0001F600 Всё работает!!!!',
                 'С задачей поставленной справился ты! Юный подаван.',
                 'Готово! Готовься к новому заданию!',
                 'Можно и по-пиву!'),
    'reviewing': ('Работа взята на проверку ревьюером.',
                  'Проверка включена.',
                  'Работа на проверке.',
                  'Жди правки.',
                  'Твою работу всзял проверять ментор.'),
    'rejected': ('Работа проверена, в ней нашлись ошибки.',
                 'Нерасслабляться, правки пришли!',
                 'Зря расслабил булки, есть ошибки в работе!',
                 'Вперёд на правку исправлений!',
                 'А вот и замечания подъехали!',
                 'Пора исправлять замечания.')
}
