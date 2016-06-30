#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, time, base64, hashlib, logging, json
import markdown

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

@view('blog_view.html')
@get('/blog/:blog_id')
def blog_view(blog_id):
    if not _id_check(blog_id):
        raise notfound()

    blog = Blog.get(blog_id)
    if not blog:
        raise notfound()
    tags = Tag.find_all()
    blog.html_content = markdown.markdown(blog.content)
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
@interceptor('/manage/')
def manage_interceptor(next):
    logging.info('try to bind user from session cookie...')
    user = None
    cookie = ctx.request.cookies.get(_COOKIE_NAME)
    logging.info(ctx.request.cookies)
    if cookie:
        logging.info('parse session cookie...')
        user = parse_signed_cookie(cookie)
        if user:
            logging.info('bind user <%s> to session...' % user.name)
    ctx.request.user = user
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
@view('/manage/blog_edit_list.html')
@get('/manage/blog_edit')
def blog_edit_list():
    blogs = Blog.find_all()
    for blog in blogs:
        blog.load_tags = json.loads(blog.tags)
    return dict(blogs=blogs)
# blog edit page
@view('/manage/blog_edit.html')
@get('/manage/blog_edit/:blog_id')
def blog_edit(blog_id):
    if not _id_check(blog_id):
        raise notfound("Blog not found!")
    return dict()


# photo create page
@view('/manage/photo_edit.html')
@get('/manage/photo_create')
def photo_create():
    return dict()
# photo list page
@view('/manage/photo_edit_list.html')
@get('/manage/photo_edit')
def photo_edit_list():
    photos = Photo.find_all()
    return dict(photos=photos)
# photo edit page
@view('/manage/photo_edit.html')
@get('/manage/photo_edit/:photo_id')
def photo_edit(photo_id):
    if not _id_check(photo_id):
        raise notfound("Photo not found!")
    return dict()


#=============================================
# API
#=============================================
#------------------------
### admin login on POST
@api
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

#--------------------------
### create or edit blog
def _add_blog_to_tag(blog_id, tag_name):
    """
    given a blog_id and tag_name, add the blog_id into tag table's `blogs` list.
    """
    this_tag = Tag.get(tag_name)
    if this_tag is None:
        this_tag = Tag(tag_name=tag_name, blogs=json.dumps([blog_id]), count=1)
        this_tag.insert()
    else:
        blog_list = json.loads(this_tag.blogs)
        blog_list.append(blog_id)
        this_tag.blogs = json.dumps(blog_list)
        this_tag.count += 1
        this_tag.update()

def _remove_blog_from_tag(blog_id, tag_name):
    this_tag = Tag.get(tag_name)
    if this_tag is None:
        return
    else:
        blog_list = json.loads(this_tag.blogs)
        blog_list.remove(blog_id)
        this_tag.blogs = json.dumps(blog_list)
        this_tag.count -= 1
        this_tag.update()

@api
@get('/manage/api/blog_get/:blog_id')
def api_blog_get(blog_id):
    if not _id_check(blog_id):
        raise APIValueError("API Request Error from api_blog_get()!")
    blog = Blog.get(blog_id)
    blog.tags = json.loads(blog.tags)
    if blog is None:
        raise APIResourceNotFoundError("Blog_ID Error!!")
    return blog

@api
@get('/manage/api/photo_get/:photo_id')
def api_photo_get(photo_id):
    if not _id_check(photo_id):
        raise APIValueError("API Request Error from api_photo_get()!")
    photo = Photo.get(photo_id)
    if photo is None:
        raise APIResourceNotFoundError("Photo_ID Error!!")
    return photo


@api
@post('/manage/api/blog_create')
def api_blog_create():
    check_admin()
    i = ctx.request.input(blogTitle="", blogTags="", blogSummary="", blogContent="")
    title = i.blogTitle.strip()
    tags = [tag.strip() for tag in i.blogTags.replace(',',';').split(';')]
    if not tags[-1]:
        tags.pop(-1)
    summary = i.blogSummary.strip()
    content = i.blogContent.strip()

    blog = Blog(title=title, tags=json.dumps(tags), summary=summary, content=content)
    blog.insert()
    for tag in tags:
        _add_blog_to_tag(blog.id, tag)
    return blog


@api
@post('/manage/api/blog_edit/:blog_id')
def api_blog_edit(blog_id):
    check_admin()
    i = ctx.request.input(blogTitle="", blogTags="", blogSummary="", blogContent="")
    title = i.blogTitle.strip()
    new_tags = [tag.strip() for tag in i.blogTags.replace(',',';').split(';')]
    if not new_tags[-1]:
        new_tags.pop(-1)
    summary = i.blogSummary.strip()
    content = i.blogContent.strip()

    blog = Blog.get(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    old_tags = json.loads(blog.tags)

    blog.title = title
    blog.tags = json.dumps(new_tags)
    blog.summary = summary
    blog.content =content
    blog.update()

    if old_tags == new_tags:
        return blog

    # tags has been change
    for new_tag in new_tags:
        if new_tag in old_tags:
            new_tags.remove(new_tag)
            old_tags.remove(new_tag)
    # delete this blog from old_tags
    for tag in old_tags:
        _remove_blog_from_tag(blog_id, tag)
    # add this blog to new_tags
    for tag in new_tags:
        _add_blog_to_tag(blog_id, tag)
    return blog

#--------------------------
### create or edit photo
@api
@post('/manage/api/photo_create')
def api_photo_create():
    check_admin()
    i = ctx.request.input(photoTitle="", photoDescript="", photoPath="", photoLocation="", photoLoc_lat="0", photoLoc_lng="0")
    title = i.photoTitle.strip()
    descript = i.photoDescript.strip()
    path = i.photoPath.strip()
    loc_name = i.photoLocation.strip()
    loc_lat = float(i.photoLoc_lat.strip())
    loc_lng = float(i.photoLoc_lng.strip())

    photo = Photo(title=title, descript=descript, path=path, loc_name=loc_name,
                  loc_lat=loc_lat, loc_lng=loc_lng)
    photo.insert()
    return photo


@api
@post('/manage/api/photo_edit/:photo_id')
def api_photo_edit(photo_id):
    check_admin()
    i = ctx.request.input(photoTitle="", photoDescript="", photoPath="", photoLocation="", photoLoc_lat="0", photoLoc_lng="0")
    title = i.photoTitle.strip()
    descript = i.photoDescript.strip()
    path = i.photoPath.strip()
    loc_name = i.photoLocation.strip()
    loc_lat = float(i.photoLoc_lat.strip())
    loc_lng = float(i.photoLoc_lng.strip())

    photo = Photo.get(photo_id)
    if photo is None:
        raise APIResourceNotFoundError('Photo')

    photo.title = title
    photo.descript = descript
    photo.path = path
    photo.loc_name = loc_name
    photo.loc_lat = loc_lat
    photo.loc_lng = loc_lng
    photo.update()
    return photo