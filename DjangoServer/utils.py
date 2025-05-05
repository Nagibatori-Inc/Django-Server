def user_directory_path(instance, filename):
    return 'adverts/images/user_{0}/{1}'.format(instance.user.id, filename)