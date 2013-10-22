import django.dispatch
films_merged = django.dispatch.Signal( providing_args=["saved_film_id", "removed_film_id"])

