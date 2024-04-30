from accounts.models import UserDatabase
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.shortcuts import render
from .utils import get_news, get_news_categories, get_post
from panel.forms import NewsData, NewsCategory
from .base import BaseEndpoint, Get, BaseFormEndpoint
import urllib

class NewsList(Get, BaseEndpoint):
    category: str = str()
    params: list = ["category", "sorting", "source", "keyword", "dateFrom", "dateTo"]
    sorting: str = str()
    source: str = str()
    keyword: str = str()
    dateFrom: str = str()
    dateTo: str = str()

    @property
    def page(self):
        current_page = self.request.GET.get('page')
        return max(1, int(current_page or 1))
    
    @property
    def category_list(self):
        return self.category.split("; ")

    def from_payload(self, param: str):
        if (result := self.request.GET.get(param)):
            setattr(self, param, result)
        return result
    
    def from_cookies(self, param: str):
        if (result := urllib.parse.unquote(self.request.COOKIES.get(param, ""))):
            setattr(self, param, result)
        return result

    def get_param(self, param: str):
        self.from_payload(param) or self.from_cookies(param) or setattr(self, param, "")
    
    def get_paginator(self, per_page):
        paginator = Paginator(self.news, per_page)
        return paginator.get_page(self.page)

    def handle_request(self):
        per_page=200
        for param in self.params:
            self.get_param(param)
        params = {param: getattr(self, param) for param in self.params}
        self.news = get_news(
            rights=self.current_project,
            **params
        )
        self.page_obj = self.get_paginator(per_page)
        unsorted_categories = get_news_categories(self.current_project)
        selected_categories = [cat for cat in unsorted_categories if cat['channel'] in self.category_list]
        unselected_categories = [cat for cat in unsorted_categories if cat['channel'] not in self.category_list]
        enumerated_categories = [
            (i+1, cat) 
            for i, cat 
            in enumerate(
                [
                    *sorted(
                        selected_categories, 
                        key=lambda cat: cat['channel']
                    ),
                    *sorted(
                        unselected_categories, 
                        key=lambda cat: cat['channel']
                    )                        
                ]
            )
        ]
        context = {
            "news": self.news[per_page*(self.page-1):per_page*self.page], 
            "news_len": len(self.news),
            "enumerated_categories": enumerated_categories, 
            "category_list": self.category_list, 
            "category": self.category, 
            "keyword": self.keyword, 
            "dateFrom": self.dateFrom,
            "dateTo": self.dateTo,
            "sorting": self.sorting,
            "source": self.source,
            "rights":self.current_project,
            "page":self.page_obj
        }
        return render(self.request, 'adminpanel/news.html', context)

class NewsListAPI(NewsList, BaseFormEndpoint):
    form_template = NewsCategory
    payload_params: list = ["category", "sorting", "keyword"]
    def get_param(self, param: str):
        if param in self.payload_params:
            self.from_payload(param)
        else:
            self.from_payload(param) or self.from_cookies(param) or setattr(self, param, "")
    
    def response_middleware(self, response):
        if self.category_list:
            category_encoded = self.category.encode('utf-8')
            category_encoded_urlsafe = urllib.parse.quote(category_encoded)
            UserDatabase.update_favourites(self.request.COOKIES.get('username'), self.category)
            response.set_cookie('category', category_encoded_urlsafe, expires=datetime.now()+timedelta(days=30))
        if not self.category_list:
            response.delete_cookie('category')
        response.set_cookie('sorting', self.sorting, expires=datetime.now()+timedelta(days=30))
        response.set_cookie('source', self.source, expires=datetime.now()+timedelta(days=30))
        keyword_encoded = self.keyword.encode('utf-8')
        keyword_encoded_urlsafe = urllib.parse.quote(keyword_encoded)
        response.set_cookie('keyword', keyword_encoded_urlsafe, expires=datetime.now()+timedelta(days=30))
        # response.set_cookie('dateFrom', self.dateFrom, expires=datetime.now()+timedelta(days=30))
        # response.set_cookie('dateTo', self.dateTo, expires=datetime.now()+timedelta(days=30))


class NewsInfo(Get, BaseFormEndpoint):
    form_template = NewsData
    media_array: list = []
    photo_amount: int = 0

    def get_newsletter(self):
        newsletter_id = self.request.GET.get('id')
        return get_post(newsletter_id=newsletter_id, number_flag=False)

    def append_link(self, link):
        result = link[1:] if link[0] == "/" else link
        self.media_array.append(result)

    def handle_request(self):
        newsletter = self.get_newsletter()
        if newsletter.data != '' and newsletter.data != 'None' :
            media_links = newsletter.data.split("|||")
            for link in media_links:
                self.append_link(link)
                self.photo_amount += 1
        context = {
            "newsletter": newsletter,
            "categories": get_news_categories(self.current_project),
            "photo_amount": self.photo_amount,
            "media_array": self.media_array,
            "project": self.current_project
        }
        return render(self.request, 'adminpanel/edit_news.html', context)
