**MAIN - done!**
  (future implementation of tag/category should be simple)

**AUTH**
  * revise token strategy for reset!
  * crossing tokens? (possible? desirable?)

**DASH**
* revise macros, form macros and use modern system for rendering...
* /delete-account view in auth to be destroyed                    --
  (set it to admin-or-self)                                       --
  (links?)                                                        ¿?
* revise before_request in auth
* user_forms macro is not very good (implies table, can be empty, ...)

* ROLES AND CONFIRMATION                                          !!
  * define better (there should be one more role)                 --
  * write better decorators                                       --
  * error in decorator when anonymous (no confirmed attribute!)   --
  * revise auth-- and dash (and forms and templates), decorators, etc. --
  * user_model testing!!
  * somewhat messy...
    (for example, users should be removed some data when banished)
    (and signup of guests should be implemented)
  * is main administrator identity checked just once? (it should)

* FORMS
  * (dash) revise afterwards
  * form-wide errors?
  * StopValidation?


* revise everything is Unicode!
* revise import system
* revise mailing system
* flask_ or flask.ext. ??
* rethink HTTP methods
* (future problem) cascade deletes? what happens with posts/comments by deleted users?
  (maybe you should just not delete them, but the posts/comments first)
* do you really want to...?

  (check http://flask.pocoo.org/snippets/63/)
* flash messaging (also in decorators)
* better dashboard definition (what happens if no username?)
* revise helpers
* list of forbidden usernames and slugs (urls!)
* validation unit tests???
* revise configuration!!
* Regexp subclasses?
* redirection with classes?
...

is it the time to...
* bootstrap? -> from CDN?

it is definitely the time to...
* revise the docs!
* revise the unit tests!
* even unit test... helpers!

...

slugs: http://flask.pocoo.org/snippets/5/
Flask-Cache: http://pythonhosted.org/Flask-Cache/
