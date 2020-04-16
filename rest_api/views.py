import logging

from django.core.validators import ValidationError
from requests import HTTPError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_api.permissions import OnlyAPIPermission, ApiKeyThrottle
from rest_api.serializers import WeatherSerializer
from rest_api.validators import lang_validator, units_validator, days_validator, ip_validator, coordinates_validator

from rest_api.helpers import (current_weather_data_helper, daily_weather_data_helper, reverse_geocode_data_helper,
                              forward_geocode_data_helper, api_exception_helper)

from rest_api.providers import (ip_info_handler, current_weather_provider, daily_weather_provider,
                                reverse_geocode_handler, forward_geocode_handler)


class CurrentWeatherView(APIView):
    permission_classes = [OnlyAPIPermission]
    throttle_classes = [ApiKeyThrottle]

    def get(self, request):
        try:
            city = self.request.GET.get('city')
            latitude = coordinates_validator(self.request.GET.get('lat'))
            longitude = coordinates_validator(self.request.GET.get('lon'))
            ip_address = ip_validator(self.request.GET.get('ip'))
            lang = lang_validator(self.request.GET.get('lang'))
            units = units_validator(self.request.GET.get('units'))

        except ValidationError as error:
            logging.error(error.message)
            return api_exception_helper(error.message, error.code)

        try:
            if city:
                geocode_data = forward_geocode_data_helper(forward_geocode_handler(city))
                wb_data = current_weather_provider(lat=geocode_data['lat'], lon=geocode_data['lon'],
                                                   units=units, lang=lang)

                weather_data, location_data = current_weather_data_helper(wb_data)
                location_data['address'] = geocode_data['address']

            elif latitude and longitude:
                wb_data = current_weather_provider(lat=latitude, lon=longitude, units=units, lang=lang)
                weather_data, location_data = current_weather_data_helper(wb_data)

                geocode_data = reverse_geocode_handler(lat=latitude, lon=longitude)
                location_data['address'] = reverse_geocode_data_helper(geocode_data)

            elif ip_address:
                ip_info = ip_info_handler(ip_address)
                wb_data = current_weather_provider(lat=ip_info.latitude, lon=ip_info.longitude, units=units, lang=lang)
                weather_data, location_data = current_weather_data_helper(wb_data)

                geocode_data = reverse_geocode_handler(lat=ip_info.latitude, lon=ip_info.longitude)
                location_data['address'] = reverse_geocode_data_helper(geocode_data)

            else:
                error_message = 'Invalid parameters.'
                logging.error(error_message)
                return api_exception_helper(error_message, status.HTTP_400_BAD_REQUEST)

        except HTTPError as error:
            logging.error(error)
            return api_exception_helper('Internal server error.', status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = WeatherSerializer(data={'location': location_data, 'weather': weather_data})

        if serializer.is_valid():
            return Response(serializer.data)

        logging.error(serializer.errors)
        return api_exception_helper('Internal server error.', status.HTTP_500_INTERNAL_SERVER_ERROR)


class DailyWeatherView(APIView):
    permission_classes = [OnlyAPIPermission]
    throttle_classes = [ApiKeyThrottle]

    def get(self, request):
        try:
            city = self.request.GET.get('city')
            latitude = coordinates_validator(self.request.GET.get('lat'))
            longitude = coordinates_validator(self.request.GET.get('lon'))
            ip_address = ip_validator(self.request.GET.get('ip'))
            days = days_validator(self.request.GET.get('days'))
            lang = lang_validator(self.request.GET.get('lang'))
            units = units_validator(self.request.GET.get('units'))

        except ValidationError as error:
            logging.error(error.message)
            return api_exception_helper(error.message, error.code)

        try:
            if city:
                geocode_data = forward_geocode_data_helper(forward_geocode_handler(city))
                wb_data = daily_weather_provider(lat=geocode_data['lat'], lon=geocode_data['lon'],
                                                 units=units, lang=lang, days=days)

                weather_data, location_data = daily_weather_data_helper(wb_data)
                location_data['address'] = geocode_data['address']

            elif latitude and longitude:
                wb_data = daily_weather_provider(lat=latitude, lon=longitude, units=units, lang=lang, days=days)
                weather_data, location_data = daily_weather_data_helper(wb_data)

                geocode_data = reverse_geocode_handler(lat=latitude, lon=longitude)
                location_data['address'] = reverse_geocode_data_helper(geocode_data)

            elif ip_address:
                ip_info = ip_info_handler(ip_address)
                wb_data = daily_weather_provider(lat=ip_info.latitude, lon=ip_info.longitude,
                                                 units=units, lang=lang, days=days)
                weather_data, location_data = daily_weather_data_helper(wb_data)

                geocode_data = reverse_geocode_handler(lat=ip_info.latitude, lon=ip_info.longitude)
                location_data['address'] = reverse_geocode_data_helper(geocode_data)

            else:
                error_message = 'Invalid parameters.'
                logging.error(error_message)
                return api_exception_helper(error_message, status.HTTP_400_BAD_REQUEST)

        except HTTPError as error:
            logging.error(error)
            return api_exception_helper('Internal server error.', status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = WeatherSerializer(data={'location': location_data, 'weather': weather_data})

        if serializer.is_valid():
            return Response(serializer.data)

        logging.error(serializer.errors)
        return api_exception_helper('Internal server error.', status.HTTP_500_INTERNAL_SERVER_ERROR)
