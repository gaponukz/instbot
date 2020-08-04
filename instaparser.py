''' Parsing instagram data for bot '''

from datetime import datetime, date
import requests
import json

from typing import (
    Callable, List, Dict, Any
)

class InstaUser(object):
    ''' Get all data about instagarm account '''
    def __init__(self, account: str) -> None:
        base_url = 'https://instagram.com'
        request = requests.get(f'{base_url}/{account}/?__a=1')
        self.account = account
        self.data = json.loads(request.text)['graphql']['user']

        self.id = self.data['id']
        self.biography = self.data['biography']
        self.external_url = self.data['external_url']
        self.followed_count = self.data['edge_followed_by']['count']
        self.follow_count = self.data['edge_follow']['count']
        self.full_name = self.data['full_name']
        self.is_public = not self.data['is_private']
        self.is_business_account = self.data['is_business_account']
        self.business_category_name = self.data['business_category_name']
        self.category_enum = self.data['category_enum']
        self.profile_pic_url = self.data['profile_pic_url_hd']
        self.connected_fb_page = self.data['connected_fb_page']
        self.posts_count = self.data['edge_owner_to_timeline_media']['count']

    def get_posts(self) -> List:
        list_of_posts = []

        for item in self.data['edge_owner_to_timeline_media']['edges']:
            list_of_posts.append(f"https://instagram.com/p/{item['node']['shortcode']}")

        return list(map(Post, list_of_posts))

    def __str__(self) -> str:
        return self.account

class Post(object):
    def __init__(self, url: str) -> None:
        request = requests.get(f'{url}/?__a=1') # https://www.instagram.com/p/{code}/?__a=1
        self.data = json.loads(request.text)['graphql']['shortcode_media']

        self.id = self.data['id']
        self.location = self.data['location']
        self.date = normal_time(self.data['taken_at_timestamp'])
        self.dimensions = [self.data['dimensions']['height'], self.data['dimensions']['width']]
        self.display_url = self.data['display_url']
        self.is_video = self.data['is_video']

        if self.is_video:
            self.video_url = self.data['video_url']
            self.has_audio = self.data['has_audio']
            self.video_view_count = self.data['video_view_count']

        if self.data['edge_media_to_caption']['edges']:
            self.description = self.data['edge_media_to_caption']['edges'][0]['node']['text']

        self.comment_count = self.data['edge_media_to_parent_comment']['count']
        self.likes_count = self.data['edge_media_preview_like']['count']

    @staticmethod
    def __get_data(post: Dict) -> Dict:
        post, imgs_data = post['node'], []

        try:
            for edge in post['edge_sidecar_to_children']['edges']:
                imgs_data.append(edge['node']['display_url'])      
        except:
            imgs_data.append(post['display_url'])

        return {
            'post_url': f"https://www.instagram.com/p/{post['shortcode']}",
            'display_url': post['display_url'],
            'is_video': post['is_video'],
            'date':normal_time( post['taken_at_timestamp']),
            'description': '' if not post['edge_media_to_caption']['edges'] \
                else post['edge_media_to_caption']['edges'][0]['node']['text'],
            'comment_count': post['edge_media_to_comment']['count'],
            'likes_count': post['edge_media_preview_like']['count'],

            'size': [post['dimensions']['height'], post['dimensions']['width']],
            'images': imgs_data
        }

    @staticmethod
    def generate_post(account: str) -> Dict[str, str]:
        request = requests.get(f'https://www.instagram.com/{account}/?__a=1')
        user_id = json.loads(request.text)['graphql']['user']['id']
        request_url = f'https://www.instagram.com/graphql/query/?query_id=17888483320059182&id={user_id}&first=294'
        request = json.loads(requests.get(request_url).text)

        data = request['data']['user']['edge_owner_to_timeline_media']
        end_cursor = data['page_info']['end_cursor']

        for post in data['edges']:
            yield Post.__get_data(post)

        while data['page_info']['has_next_page']:
            request = requests.get(f'{request_url}&after={end_cursor}')
            data = json.loads(request.text)['data']['user']['edge_owner_to_timeline_media']

            for post in data['edges']:
                yield Post.__get_data(post)

            end_cursor = data['page_info']['end_cursor']

    def get_comments(self) -> List[Dict[str, Any]]:
        comment_data = []
        for comment in self.data['edge_media_to_parent_comment']['edges']:
            comment_data.append({
                'text': comment['node']['text'],
                'date': normal_time(comment['node']['created_at']),
                'is_spam': comment['node']['did_report_as_spam'],
                'owner': InstaUser(comment['node']['owner']['username']),
                'likes_count': comment['node']['edge_liked_by']['count']
            })

        return comment_data

# some func for datetime
def normal_time(date: int) -> str:
	return datetime.fromtimestamp(date).strftime('%d.%m.%Y')

def get_date(date_str: str) -> datetime.date:
	date_list = date_str.split('.')

	return date(
		int(date_list[2]),
		int(date_list[1]),
		int(date_list[0])
	)

# def for bot
def filter_by_date(posts, _from: str,  _to: str):
	_from, _to = get_date(_from), get_date(_to)
	filter_post = [
		post for post in posts if _from >= post['date'] >= _to
	]

	return filter_post

def sort(posts = None, by: str = None): # sort(posts, by = 'likes')
    sort_by = 'comment_count' if by == 'comments' else 'likes_count'
    return sorted(posts, key = lambda post: post[sort_by])[::-1]

def get_posts(account: str):
	account, data = InstaUser(account), []
	post = Post.generate_post(account.account)

	for _ in range(account.posts_count):
		data.append(post.__next__())

	return data