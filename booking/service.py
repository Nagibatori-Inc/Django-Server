from booking.models import Advert, AdvertStatus


class AdvertService:
    """
    Класс, реализующий бизнес логику работы с объявлениями
    
    Methods:
        - activate: Активирует объявление
        - deactivate: Деактивирует объявление
        - advertise: Публикация объявления
        - change: изменение объявления (например, изменение описания)
    """
    
    def __init__(self, advert: Advert):
        self.__advert = advert
        
    def activate(self) -> None:
        self.advert.status = AdvertStatus.ACTIVE
        self.advert.save()
        
    def deactivate(self) -> None:
        self.advert.status = AdvertStatus.DISABLED
        self.advert.save()
        
    def change(self, changed_data: dict) -> None: # changed_data пока имеет тип dict, в дальнейшем будет объектом валидационной схемы
        advert: Advert = self.advert
        
        advert.title = changed_data['title']
        advert.description = changed_data['description']
        advert.price = changed_data['price']
        advert.phone = changed_data['phone']
        advert.promotion = changed_data['promotion']
        advert.activated_at = changed_data['activated_at']
        
        advert.save()
        
    def remove(self):
        advert: Advert = self.advert
        advert.delete()
        
    # TODO: ВСЕ объявления должны публиковаться через этот метод
    @staticmethod
    def advertise(
        title: str,
        description: str,
        price: float,
        phone: str,
        promotion: str = None,
    ):
        """
        Метод реализации логики подачи объявления (Публикация объявления)
        
        Args:
            title (str): Название объявления
            description (str): Текст объявления
            price (float): Стоимость услуги
            phone (str): Контакты - телефон
            promotion (str, optional): Данные о продвижении объявления. Может быть None

        Returns:
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
    