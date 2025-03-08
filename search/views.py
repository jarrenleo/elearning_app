from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


@login_required
def search_view(request):
    # Get the query from the request
    query = request.GET.get("query", "")
    # Store the results
    results = []

    # If the query is not empty
    if query:
        # Get the user model
        User = get_user_model()
        # Search for users
        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )[:5]

        # Format user results
        for user in users:
            results.append(
                {
                    "name": user.get_full_name(),
                    "username": user.username,
                    "role": user.role.capitalize(),
                }
            )

        # Render the search results
        return render(
            request, "search/search_results.html", {"results": results, "query": query}
        )
