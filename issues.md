**MAIN**
  * Simplify `errors.py`?
  * Revise templates (again).
  * (future implementation of tag/category should be simple...)

**AUTH**
  * revise email sending (kind of ugly)
  * revise token strategy for reset!
  * crossing tokens (possible? desirable?)

**USER**
* user list: more beautiful table
  * big link, border, padding...
  * ticks for confirmation!
  * all-purpose macro for deletion confirmation ('are you sure?')
* edit & role: could be better defined...
* delete view validation (check it's a guest)
* URL validation within profile (add http?)
* redirection strategy (not always profile but referrer!)

**POST**
* delete post: has been moved to `models.py`.
  should revise and do something similar with users?
* need decorators!
* cancel button!
* what about page?

**CATEGORY & TAG**
* nicer interface!
* study this:
  `AmbiguousForeignKeysError: Could not determine join condition between parent/child tables on relationship Category.posts - there are multiple foreign key paths linking the tables. Specify the 'foreign_keys' argument, providing a list of those columns which should be counted as containing a foreign key reference to the parent table.`
  [ Error was solved (?) within Post.category (foreign_keys=...) ]

* changing backref to back_populates (it's clearer)
  I still keep it for author, because it's made with a mixin...
  Just now it's a bit of a mess...............


**********************************
# i'm here

* go on with the generic link idea (users?)

**********************************

* revise macros, form macros and use modern system for rendering...
* user_forms macro is not very good (implies table, can be empty, ...)

* revise decorators
* user_model, forms, ... testing!!

* FORMS
  * form-wide errors?
  * StopValidation?
  * InputRequired!!

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

* revise helpers
* list of forbidden usernames and slugs (urls!)
* validation unit tests???
* revise configuration!!
* Regexp subclasses?
* redirection with classes?

it is definitely the time to...
* revise the docs!
* revise the unit tests!
* even unit test... helpers!

...

slugs: http://flask.pocoo.org/snippets/5/
Flask-Cache: http://pythonhosted.org/Flask-Cache/
