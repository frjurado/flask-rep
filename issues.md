**MAIN**
  * Simplify `errors.py`?
  * Revise templates (again)

**AUTH**
  * revise email sending (kind of ugly)
  * revise token strategy for reset!
  * crossing tokens (possible? desirable?)

**USER**
* user list: more beautiful table
  * big link, border, padding...
  * ticks for confirmation!
  * all-purpose macro for deletion confirmation ('are you sure?')
  * AJAX forms.
* edit & role: could be better defined...
* delete view validation (check it's a guest)
* URL validation within profile (add http?)
* redirection strategy (not always profile but referrer!)

**POST**
* delete post: has been moved to `models/content.py`.
  should revise and do something similar with users?
* need decorators!
* cancel button!
* what about page? status?

**CATEGORY & TAG**
* nicer interface!
* study this: `AmbiguousForeignKeysError`
  [ Error was solved (?) within Post.category (foreign_keys=...) ]
* backref vs. back_populates (what is clearer?)
* go on with the generic link idea (users?)


**********************************
# i'm here

**IMAGE**
* Image class, with MainContentMixin, filename, alternative & caption,
  * plus many-to-many relationship to Post.
    * before implementing the rest of the relationships,
      * re-implement simple image uploading;
      * try AJAX image uploading.
  * plus many-to-one relationship to Category!
  * plus both Post and Category have a many-to-one relationship to Image
    (main_image_id or something like that) !!!


**reforming MODELS**
* should define fucking tests!
* Post/Page is no longer hierarchical
* Post/Page status has to be implemented
* Page option has to be implemented
* Category is hierarchical, but not with a mixin
  * The problem arose when trying to apply HierarchicalMixin to Post
  * Querying anything became impossible, as when it mapped the tables
    `Table object has no attribute id` arised...
  * Check that out!


**********************************
* revise macros, form macros and use modern system for rendering...
* user_forms macro is not very good (implies table, can be empty, ...)
* revise decorators
* user_model, forms, ... testing!!

* FORMS
  * form-wide errors?
  * StopValidation?
  * InputRequired!!
  * validation unit tests???

* revise everything is Unicode! (encode declaration!)
* revise import system
* revise mailing system
* flask_ or flask.ext. ??

* rethink HTTP methods

* (future problem) cascade deletes? what happens with posts/comments by deleted users?
  (maybe you should just not delete them, but the posts/comments first)
* do you really want to...?

* flash messaging (also in decorators)
* revise helpers
* list of forbidden usernames and slugs (urls!)
* revise configuration
* Regexp subclasses?
* redirection with classes?

it is definitely the time to...
* revise the docs!
* revise the unit tests!
* unit test helpers!

...

secure back redirects: http://flask.pocoo.org/snippets/63/
slugs: http://flask.pocoo.org/snippets/5/
Flask-Cache: http://pythonhosted.org/Flask-Cache/
