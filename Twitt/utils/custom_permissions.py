from rest_framework.permissions import BasePermission


class CanPerformRetrieveOrUpdateOrDelete(BasePermission):
    """
    Custom permission class to determine if a user has permission to retrieve, update, or delete a specific post.
    Permission is granted if the user is an admin or if the post with the specified post_id belongs to the user.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        post_id = request.query_params.get("post_id")
        post = request.user.posts.filter(id=post_id).exists()

        if request.user.is_admin or post:

            return True


class CanDeleteComment(BasePermission):
    """
    Custom permission class to determine if a user has permission to delete a specific comment.
    Permission is granted if the comment with the specified comment_id belongs to the user.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        comment_id = request.data.get("comment_id")
        comment = request.user.all_posts_comment.filter(id=comment_id).exists()

        if comment:
            return True
