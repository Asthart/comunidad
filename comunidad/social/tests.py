from django.test import TestCase

# Create your tests here.
  # """
  #   Default 404 handler.
  #
  #   Templates: :template:`404.html`
  #   Context:
  #       request_path
  #           The path of the requested URL (e.g., '/app/pages/bad_page/'). It's
  #           quoted to prevent a content injection attack.
  #       exception
  #           The message from the exception which triggered the 404 (if one was
  #           supplied), or the exception class name
  #   """
  #   exception_repr = exception.__class__.__name__
  #   # Try to get an "interesting" exception message, if any (and not the ugly
  #   # Resolver404 dictionary)
  #   try:
  #       message = exception.args[0]
  #   except (AttributeError, IndexError):
  #       pass
  #   else:
  #       if isinstance(message, str):
  #           exception_repr = message
  #   context = {
  #       "request_path": quote(request.path),
  #       "exception": exception_repr,
  #   }
  #   try:
  #       template = loader.get_template(template_name)
  #       body = template.render(context, request)
  #   except TemplateDoesNotExist:
  #       if template_name != ERROR_404_TEMPLATE_NAME:
  #           # Reraise if it's a missing custom template.
  #           raise
  #       # Render template (even though there are no substitutions) to allow
  #       # inspecting the context in tests.
  #       template = Engine().from_string(
  #           ERROR_PAGE_TEMPLATE
  #           % {
  #               "title": "Not Found",
  #               "details": "The requested resource was not found on this server.",
  #           },
  #       )
  #       body = template.render(Context(context))
  #   return HttpResponseNotFound(body)




























    #
    #   """
    # 500 error handler.
    #
    # Templates: :template:`500.html`
    # Context: None
    # """
    # try:
    #     template = loader.get_template(template_name)
    # except TemplateDoesNotExist:
    #     if template_name != ERROR_500_TEMPLATE_NAME:
    #         # Reraise if it's a missing custom template.
    #         raise
    #     return HttpResponseServerError(
    #         ERROR_PAGE_TEMPLATE % {"title": "Server Error (500)", "details": ""},
    #     )
    # return HttpResponseServerError(template.render())
