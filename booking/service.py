from booking.models import Advert


class AdvertService:
    """
    Класс, реализующий бизнес логику работы с объявлениями
    
    :Methods:
        - activate: Активирует бъявление
        - deactivate: Деактивирует объявление
        - advertise: Публикация объявления
    """
    
    def __init__(self, advert: Advert):
        self.__advert = advert
        
    def activate(self) -> None:
        self.__advert.is_active = True
        self.__advert.save()
        
    def deactivate(self) -> None:
        self.__advert.is_active = False
        self.__advert.save()
        
    # TODO: ВСЕ объявления должны публиковаться через этот метод
    @staticmethod
    def advertise(
        title: str,
        description: str,
        price: float,
        phone: str,
        promotion: str = None,
    ) -> AdvertService:
        """
        Метод реализации логики подачи объявления (Публикация объявления)
        
        :Args:
            title (str): Название объявления
            description (str): Текст объявления
            price (float): Стоимость улсуги
            phone (str): Контакты - телефон
            promotion (str, optional): Данные о продвижении объявления. Может быть None

        :Returns:
            AdvertService: объект сервисной логики работы с объявлениями
        """
        
        return AdvertService(
            Advert.objects.create(
                title=title,
                description=description,
                price=price,
                phone=phone,
                promotion=promotion,
            )
        )
        
    @property
    def advert(self):
        return self.__advert
    