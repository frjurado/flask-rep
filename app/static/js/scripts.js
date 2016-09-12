//
//
//


// variable difinitions //
// -------------------- //
var CSRFToken = "{{ csrf_token() }}"
var postView = ( typeof commentForm !== 'undefined' );


// function definitions //
// -------------------- //

// show & hide
function show(element) { element.removeClass("hidden"); }
function hide(element) { element.addClass("hidden"); }

// onHover
function onHover(hoverElement, showElement) {
  $(hoverElement).hover(
    function() { show( $(showElement, this) ); },
    function() { hide( $(showElement, this) ); }
  );
}

// createCommentForm
function createCommentForm(container, parent_id) {
  var mainComment = ( typeof container === 'undefined' );
  if (mainComment) {
    container = $(".comments > .comment-form-box");
  }
  container.append(commentForm);
  var form = container.find(".commentForm");
  if (!mainComment) {
    form.attr("id", "commentForm" + parent_id);
    form.find("#parent_id").attr("value", parent_id);
    form.find("#body_md").focus();
  }
  setAjax(form, sendComment(container, mainComment));
}

// answerClick
function answerClick(elements) {
  elements.click( function(e) {
    e.preventDefault();
    // hide this answer button, show the rest of them
    show( elements );
    hide( $(this) );
    // create this form, hide the rest of them
    $(".commentForm").parent(".form-box").remove();
    var container = $(this).parent("p").siblings(".comment-form-box");
    var id = $(this).attr("id").slice(6);
    createCommentForm( container, id );
  });
}

// setAjax
function setAjax(form, success) {
  form.submit( function(e) {
    e.preventDefault();
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: "POST",
      success: success,
      error: function(error) {
        console.log(error);
      }
    });
  });
}

// statusCurtain (a success function)
function statusCurtain (curtain) {
  function success (response) {
    if (response.status) { hide(curtain); }
    else { show(curtain); }
  }
  return success;
}

// sendComment (a success function)
function sendComment ( container, mainComment=false ) {
  function success (response) {
    container.children(".form-box").remove();
    if (!mainComment) {
      show( container.siblings("p").children("a") );
      container.siblings(".comment-children").append(response.comment);
    } else {
      container.before(response.comment);
    }
    createCommentForm();
  }
  return success;
}


// set CSRF Token //
// -------------- //
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", CSRFToken)
    }
  }
});


// document ready actions
// ----------------------
$( function() {
  // hover functions
  onHover(".short-post", ".post-buttons");
  onHover(".post-main-image", ".post-buttons");
  onHover(".photo-thumbnail", ".to-clipboard");

  // post status functions
  // (post list)
  var shortPostStatusForms = $(".short-post .status-form");
  shortPostStatusForms.each( function() {
    setAjax(
      $(this),
      statusCurtain( $(this).closest(".short-post").children(".post-off") )
    );
  });
  // (post perma)
  setAjax(
    $(".post-main-image .status-form"),
    statusCurtain( $(".post-off") )
  );

  // create main comment form
  if (postView) {
    createCommentForm();
  }

  // activate answer buttons
  answerClick( $(".answer-button") );
})
