* MAIN
  * for helpers: query or abort

* avatars!!                                                       --
* links to auth changes in YOUR profile                           --
  (and to role changes if administrator)                          --
* status of "pending new email": confirmed or not?                --
  (it's confirmed... on the old email)
* what if you try to change ADMIN email?                          --
  (you can't)
* /delete-account view in auth to be destroyed                    --
  (set it to admin-or-self)                                       --
  (links?)                                                        ¿?

* signup enabled in config                                        --
  (should be done better for env variables)                       ¿?

* different token strategy?                                       --
* crossing tokens? (possible? desirable?)

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
  * (auth) email/username & old password validation as generic functions  ¿?
  * StopValidation doesn't seem to work
  * (dash) revise afterwards
  * form-wide errors?
  * user_forms macro is not very good (implies table, can be empty, ...)
  * validation unit tests?

* revise everything is Unicode!

* revise import system
* flask_ or flask.ext. ??
* rethink HTTP methods
* (future problem) cascade deletes? what happens with posts/comments by deleted users?
  (maybe you should just not delete them, but the posts/comments first)
* do you really want to...?
* revise redirection strategy
  (check http://flask.pocoo.org/snippets/63/)
* flash messaging (also in decorators)
* better dashboard definition (what happens if no username?)
* revise helpers
* list of forbidden usernames and slugs (urls!)
...

is it the time to...
* bootstrap? -> from CDN?

it is definitely the time to...
* revise the docs!
* revise the unit tests!

...

slugs: http://flask.pocoo.org/snippets/5/
Flask-Cache: http://pythonhosted.org/Flask-Cache/
