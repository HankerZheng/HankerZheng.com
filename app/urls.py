#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, time, base64, hashlib, logging

import markdown2

from transwarp.web import get, post, ctx, view, interceptor, seeother, notfound

from apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
from models import User, Blog, Photo, Tag
from config import configs, Dict

_COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret
ARCHIVE_TIME = 0
_RE_IDMATCH = re.compile('\W')  # re.search() not None when none-word in string

def get_archives(blogs=None):
    archives = []
    blogs = Blog.find_all(order='created_at DESC')
    for blog in blogs:
        archive = Dict()
        mmy = time.strftime('%B %m %Y',time.localtime(blog.created_at)).split()
        # mmy would be ['March', '03', '2016']
        archive.href = '/blogs/%s/%s' % (mmy[2], mmy[1])
        archive.time = '%s %s' % (mmy[0], mmy[2])
        archives.append(archive)
    return archives


def _id_check(id_for_check):
    str_id = str(id_for_check)
    if _RE_IDMATCH.search(str_id):
    # there is none-word word in id_for_check, fail the check
        return False
    return True

def make_signed_cookie(id, password, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, password, expires, _COOKIE_KEY)).hexdigest()]
    return '-'.join(L)

def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = User.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None

def check_admin():
    user = ctx.request.user
    if user and user.admin:
        return
    raise APIPermissionError('No permission.')


# Pagination info
def _get_page_info(item_type, where=None, page_size=10):
    page_index = 1
    try:
        page_index = int(ctx.request.get('page', '1'))
    except ValueError:
        pass

    if where:
        total = item_type.count_by(where)
    else:
        total = item_type.count_all()
    page = Page(total, page_index, page_size)
    return page

# =============================================
# Home Page
# =============================================
@view('index.html')
@get('/')
def index():
    return dict()


# =============================================
# About blogs and blog
# =============================================
#
# BLOGS display the title, created_at, tags, summary of blogs
#
@view('blogs.html')
@get('/blogs')
def blogs_all():
    page = _get_page_info(item_type=Blog, page_size=10)
    blogs = Blog.find_by('order by created_at DESC limit ?,?', page.offset, page.limit)
    tags = Tag.find_all()
    return dict(blogs=blogs, page=page, tags=tags)

@view('blogs.html')
@get('/blogs/:year/:month')
def blogs_month(year, month):
    try:
        year, month = int(year), int(month)
    except:
        raise notfound()
    page = _get_page_info(  item_type=Blog,
                            where='where cr_month = %s AND cr_year = %s order by created_at DESC'%(month, year),
                            page_size=10)    
    blogs = Blog.find_by('where cr_month = ? AND cr_year = ? order by created_at DESC limit ?,?',
                          month, year, page.offset, page.limit)
    tags = Tag.find_all()
    for blog in blogs:
        blog.html_summary = markdown2.markdown(blog.summary)
    return dict(blogs=blogs, page=page, tags=tags)

@view('blogs.html')
@get('/blogs/:year')
def blogs_year(year):
    try:
        year = int(year)
    except:
        raise notfound()
    page = _get_page_info(  item_type=Blog,
                            where='where cr_year = %s order by created_at DESC'% year,
                            page_size=10)
    blogs = Blog.find_by('where cr_year = ? order by created_at DESC limit ?,?', 
                          year, page.offset, page.limit)
    tags = Tag.find_all()
    for blog in blogs: 
        blog.html_summary = markdown2.markdown(blog.summary)
    return dict(blogs=blogs, page=page, tags=tags)

@view('blog_view.html')
@get('/blog/:year/:month/:blog_id')
def blog_view(year, month, blog_id):
    if _id_check(blog_id):
        try:    year, month = int(year), int(month)
        except: raise notfound()
    else:
        raise notfound()

    blog = Blog.get(blog_id)
    if not blog:
        raise notfound()
    if blog.cr_month != month or blog.cr_year != year:
        raise notfound()
    blog.html_content = markdown2.markdown(blog.content)
    tags = Tag.find_all()
    return dict(blog=blog, tags=tags)

# =============================================
# About photos
# =============================================
@view('photos.html')
@get('/photos')
def photos_all():
    page = _get_page_info(item_type=Photo, page_size=24)
    photos = Photo.find_by('order by created_at DESC limit ?,?',
                            page.offset, page.limit)
    return dict(photos=photos, page=page)


# =============================================
# About archives
# =============================================
#
# ARCHIVES only display the title, created_at and tags of blogs
# without the summary
#
@view('archives.html')
@get('/archives')
def archives_all():
    page = _get_page_info(item_type=Blog, page_size=15)
    blogs = Blog.find_by('order by created_at DESC limit ?,?', page.offset, page.limit)
    tags = Tag.find_all()
    return dict(blogs=blogs, page=page, tags=tags)

# =============================================
# About about.me
# =============================================
@view('about.html')
@get('/about')
def about_me():
    return dict()

# =============================================
# About admin and admin_login
# =============================================
# manage interceptor
@interceptor('/manage')
def manage_interceptor(next):
    logging.info('try to bind user from session cookie...')
    user = None
    cookie = ctx.request.cookies.get(_COOKIE_NAME)
    logging.info(ctx.request.cookies)
    expires = ctx.request.cookies.get('expires')
    if cookie:
        logging.info('parse session cookie...')
        user = parse_signed_cookie(cookie)
        if user:
            logging.info('bind user <%s> to session...' % user.name)

    if user and user.admin:
        return next()
    raise seeother('/admin_login')

# admin login on GET
@view('/manage/admin_login.html')
@get('/admin_login')
def log_in_page():
    try:
        failed = int(ctx.request.get('failed', 0))
    except:
        failed = 0
    return dict(failed=failed)
# admin login on POST
@view('/manage/admin_login.html')
@post('/admin_login')
def get_login_info():
    logging.info("In Get Login Info!")
    i = ctx.request.input(username="", password="", remember="")
    user = User.find_first("where name=?", i.username)
    if user is None:
        raise seeother("/admin_login?failed=1")
    elif user.password != i.password:
        raise seeother("/admin_login?failed=1")
    # make session cookie:
    # max_age is set to 10 min if not remember, else 7 days
    max_age = 604800 if i.remember else None
    cookie = make_signed_cookie(user.id, user.password, max_age)
    ctx.response.set_cookie(_COOKIE_NAME, cookie, max_age=max_age)
    raise seeother("/manage/index")

# admin index page
@view('/manage/index.html')
@get('/manage/index')
def manage_index():
    return dict()

# blog create page
@view('/manage/blog_edit.html')
@get('/manage/blog_create')
def blog_create():
    return dict()
# blog list page
@view('/manage/blog_list.html')
@get('/manage/blog_edit')
def blog_edit():
    return dict()
# photo edit page
@view('/manage/blog_edit.html')
@get('/manage/blog_edit/:id')
def photo_create():
    return dict()

# photo create page
@view('/manage/photo_edit.html')
@get('/manage/photo_create')
def photo_create():
    return dict()
# photo list page
@view('/manage/photos_list.html')
@get('/manage/photo_edit')
def photo_edit():
    return dict()
# photo edit page
@view('/manage/photo_edit.html')
@get('/manage/photo_edit/:id')
def photo_create():
    return dict()


# =============================================
# API
# =============================================