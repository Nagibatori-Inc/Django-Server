from model_bakery.recipe import Recipe

from authentication.models import Profile

profile_daniil = Recipe(
    Profile,
    name="Даниил",
    user__username="79183100755",
)
