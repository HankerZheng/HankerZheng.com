# HankerZheng.com

Source code of [my personal website](http://hankerzheng.com) 


#Update LOG

#####Beijing Time 2016-07-11 03:08AM, Basically finishing the design and deployment of the website!!!!

2016-07-16
=================
1. metadata added.

2. Change page_size of blogs into 7.

3. Sitemap may not end with '/'



2016-07-15
=================
1. Sitemap added.

2016-07-14
=================
1. Google Analytics added.


2016-07-13
=================
1. Photo gallery support large and small file(through 'data-bsp-large-src' attr of `<img>` tag)

2. `photo.html` no longer extended from `left_right.html`. That is, no right navbar in photo page.

3. Photo gallery changed:
    - dynamically add attr `data-bsp-large-src`. This attr is only added to the `<img>` tag whose `src` attr's value start with '/static/'
    - This change is to make it compatible with internet pic.
    - Photos store in SQL should have the path format showed below:
        - `path = 'http://.....'` Internet image
        - `path = '/static/photos/picXXX_small.jpg'` local image.
    - use `load` method to wait until the img was completely loaded, then reposition the modal.

4. Change 'magician' to 'witzard'.

2016-07-11
=================
1. Domain registered as `www.hankerzheng.com`

2. Disqus comment system added;

3. Bugs in management configuration fixed.


2016-07-10
=================
1. Deploymeng of Web App:
    - on Linux, `sudo apt-get install nginx gunicorn python-gevent supervisor mysql-server`, and `sudo apt-get install python-jinja2 python-mysql.connector`
    - on local machine, `pip install fabric`, and get `Cygwin`
    - Nginx would run as www-data user as default, therefore we should give access to web file to www-data user and group;
    - add `favicon.ico`

2. Change the structure of the project files, making `/static/photos` a soft link

3. Implement admin login through Vue.js rather than normal POST;

4. Some changes applied:
    - Right nav bar no longer stay fixed with the window;
    - Jumbotron's background-color no longer change;
    - change the font-family of blog title;
    - When ready, the window would scroll to 297 rather than 300 so that 'back-to-top' button would work from the very beginning;
    - Archive page and About page no longer have a negative margin!
    - Change the background color to make it dimmer so that it would not be a light strike during the switch between `index` and content pages; 

5. Index page!

6. Beijing Time 2016-07-11 03:08AM, Basically finishing the design and deployment of the website!!!!


2016-07-05
=================
1. Shrink `jquery.bsPhotoGallery.js`

2. Slightly change the blogstyle

3. About page logic finished, load through AJAX get() function. URL is `/static/about.txt`

4. Code highlighter added, and move showdown and highlighter to only `about.html`, `blog_view.html`, `blogs.html`


2016-07-04
=================
1. View `jquery.bsPhotoGallery.js`
    - `$.extend()` function `extend(dest,src1,src2,src3...);`
    ```javascript
    var result=$.extend({},{name:"Tom",age:21},{name:"Jerry",sex:"Boy"});
    result=={name:"Jerry",age:21,sex:"Boy"};
    ```
    - `$(selector).each(function(index, domEle))` function help search all the elements in the DOM that match the selector and do `function()` to them


2016-07-03
=================
1. What has been done today:
    - right nav side bar finished. Show `Tags`, `Friendly Links`, `Follow` and Easter Eggs.
    - apply Regular Expression search from MySQL for tag page.
    - change the Jumbotron into a special effect which may show `A programmer who can play electrical guitar`
    - Management method `DELETE` with confirm modal added(through `GET` method)
    - Management page pagination added

2. Things to be done:
    - CODE Highlight in the content
    - Home page, About page, Archives page
    - add thumbnail for every photo in the gallery

2016-07-02
=================
1. What has been done today:
    - Decide the specail color for this blog -- `#e68019` orange
    - Decide the left-right block and their content! Still put blog in the left block and make right block invisible by `.sm-hidden`
    - Basic style of blog title and blog meta infomation
    - Change the colomn type of `blogs.summary` to `mediumtext`
    - Adjust the length of `blog.title`(from 50 to 150), `blog.tags`(from 100 to 150), `photo.title`(50 to 150), `photo.loc_name`(from 50 to 150)
    - Solve the problem that the tags of one blog would disappear in the edit mode. This problem is cause by that `data.tags` got in the `jQuery.get()` is a list rather than a string(this is also the reason why `,` would be the seperator here).
    - Decide the style for `blog.content`

2. Things to be done:
    - CODE highlight in the content
    - Home page, About page, Tags page
    - add thumbnail for every photo in the gallery

2016-06-30
=================
1. After briefly reading the guidance of Vue.js, some structure of this website need to be changed:
    - The main idea of using Vue.js is to seperate front-end and back-end code. That is, back-end(by it, here means Python code in the project) don't need to worry what dict() should return, because all the info would send to front-end by AJAX
    - To make the website crawlable, we just use AJAX to the manage edit page.]
    - Since blog/photo edit page is the same page as create page, the javascript should tell the difference between the two from the URL.

2. Tag issues:
    - in `javascript`, `JSON.parse()` can't parse `\"` as `"`. The correct way to make it parse `"` is to make it `\\\"`
    - Solved by `blog.tags = json.loads(blog.tags)` before return blog in `api_blog_get()`

3. Photo issues:
    - Can't make photo title as the primary key for photos table, because we may want to change the photo title!
    - Add photo id colomn as blog.

4. Management basically finished. Deletion still needs to be added.

5. What has been done today:
    - Apply Vue.js to implement the blog/photo edit page
    - API post/get for blog/photo edit page
    - Apply front-end-side SHOWDOWN.JS to markdown the text for blog
    - add animation to `back-to-top` button

5. Things to be done:
    - Add deletion function for blogs and photos
    - CSS for blog display
    - left and right block for blig list and blog view
    - implement `READ MORE...` button without `blog.summary`


2016-06-29
=================
1. Photo gallery optimization:
    - make modal in the middle of the window;
    - 'pText' get from the `[title]` of the `<img>`, get `header` from the `[alt]` of the `<img>`;
    - pagination added; (also added for `/blogs` but still need to test)

2. Blog creatate/edit page:
    - for blog create page, information listed beblow need to be submit to the server:
        - `title`
        - `tags`
        - `summary`
        - `content`
    - for blog edit page, information listed below need to be submit to the server:
        - `id`: this may not be showed in the the page
        - `title`
        - `tags`
        - `summary`
        - `content`

3. blog creatate/edit page:
    - for blog create page, information listed beblow need to be submit to the server:
        - `title`
        - `tags`
        - `summary`
        - `content`
    - for blog edit page, information listed below need to be submit to the server:
        - `id`: this may not be showed in the the page
        - `title`
        - `tags`
        - `summary`
        - `content`


2016-06-28
=================
1. Photo gallery designed by [Michael Soriano](https://github.com/michaelsoriano/bootstrap-photo-gallery) is successfully applied. But still needs to be fixed.
    - transition animation applied to photo where mouse hovers on.
    - change the height and width dynamically by Javascript.
    - make the max col of the gallery 3

2016-06-27
=================
1. Encrypted with HMAC with key `"Hanker"`;
    ```python
    import hmac
    msg = "inputPassword"
    password = hmac.new("Hanker", msg).hexdigest()
    ```
    ```javascript
    // <script src="../static/js/md5.min.js"></script>
    msg = $("#inputPassword").val();
    password = md5(msg, "Hanker").toString();
    ```

2. Log-In with `POST` method, action on `/admin_login`. If success, redirect to `/manage/index`; if fail, redirect to `/admin_login?failed=1`

3. Log-in username is `xxxx`, log-in password is `xxxxxxxx`

4. `/manage` sites:
    - `/manage/index`: homepage for manager with 4 buttons `@view('/manage/index.html')`
    - `/manage/blog_create`: blog edit page for create `@view('/manage/blog_edit.html')`
    - `/manage/blog_edit`
    - `/manage/blog_edit/:id`
    - `/manage/photo_create`
    - `/manage/photo_edit`
    - `/manage/photo_edit/:id`

5. No need to respect the expire-time and max-age of cookie, the browser would do it for u.

    >如果不设置过期时间，则表示这个cookie生命周期为浏览器会话期间，只要关闭浏览器窗口，cookie就消失了。这种生命期为浏览会话期的cookie被称为会话cookie。会话cookie一般不保存在硬盘上而是保存在内存里。
    >如果设置了过期时间(setMaxAge(606024))，浏览器就会把cookie保存到硬盘上，关闭后再次打开浏览器，这些cookie依然有效直到超过设定的过期时间。存储在硬盘上的cookie可以在不同的浏览器进程间共享，比如两个IE窗口。而对于保存在内存的cookie，不同的浏览器有不同的处理方式。(在IE下测试通过)

6. Things for tomorrow:
    - Photo gallary: the previous failure was caused by jQurey version
    - Vue.js plug-in and change the login function
    - add blog edit and photo edit HTML files


2016-06-23
=================
1. Start with logic/backend of the website first, then the frontend.

2. website logic:
    - Main page `@view(index.html)`
    - View blog page `@view(blog_view.html)`
        - variable needed `blog`, `tags`
    - Several blogs page `@view(blogs.html)`
        - variables needed `blogs`, `page`, `tags`
    - Photo page `@view(photos.html)`
        - display thumbnail of photos
        - handle by JavaScript like it does in Bing Gallary
        - variables needed `photos`, `page`
    - About.me page `@view(about.html)`
        - the instruments i have or have had
        - the earphone/headphone i have or have had
        - the video game console i have or have had
        - the computer I have or have had
        - the phone I have or have had
        - the band I am enthusiastic about
        - the Animate I have watched
        - the book I have read 
    - Admin login page `@view(login.html)`
        - this page is isolated, url is `/manage/admin_login`
        - After log in, redirect to `/manage/blog_create`
    - Manage blog page `@view(manage.html)`


2016-03-26
=================
1.  blocks for base.html:
    - {% block title %}
    - {% block nav_bar %} - only to set 'active'
    - {% block pagetitle %} - the title for this page, in the container
    - {% block content %} - the main content of this page
    - {% block funcript %} - put functional JS here
    - list archives - every page that extends base.html should return archives
        ```javascript
        {% for archive in archives %}
        <li><a href='{{ archive.href }}'>{{ archive.time }}</a></li>
        {% endfor %}
        ```

2.  ORM usage:
    - class method:
        - `get(cls, pk)`: get item by pk  
        - `find_first(cls,where,*args)`: find by where clause, return first item found
        - `find_all(class, order, *args)`: return a list of all items in `cls.__table__`
        - `find_by(cls, where, order, *args)`: find by where clause, return all items found
        - `cout_all(cls)`: count the num of items in talbe
        - `count_by(cls, where, *args)`: count the num of items according to the where clause
    - instance method:
        - `update(self)`: update the database by the vale of the instance
        - `delete(self)`: delete item from db by item's pk
        - `insert(self)`: create a new item in db by the instance

3. Things to be done:
    - Archives Problem:
        - When dynamically update the table `blogs` in database, archives won't change. But it consumes a lot server resources to update archives whenever get a page 
        - __sol__: make it refresh every 10 min
    - Why api always comes with 'POST' method?
        - ???
    - How to access POST data from wsgi?
        - When use ctx.request.get_body(), there would be no response from server?
        - Should use ctx.request.input(name='')?


2016-03-23
=================
1.  file hierarchy tree:

    > ./  
    > +.--app/  
    > +.--static/  
    > +.--templates/  
    > +.--manage/  
    > +.--admin/  
    > +.--transwarp/

2.  HTML Framework  - Bootstrap  
    Web Framework   - Transwarp with ORM from Michael Liao  
    Template Engine - Jinja2  
    DataBase        - MySQL

3.  Items for blogs
    - Home Page - '/'
    - Blogs - '/blogs'
        - make use of disquz as the comment
        - for each blog - '/blog/:blog.cr_year/:blog.cr_month/:blog_id'
    - Photos
        - make use of disquz as the comment
        - access as a static file 
        - for each photo, use JS to view full-size image
    - archives - '/archives'
    - About Me - '/about'
    - Admin login - '/admin_login'

4.  Database name:  MyBlog

    > table - blogs  
    > table - photos  
    > table - user(only store one admin)  
    > table - tags