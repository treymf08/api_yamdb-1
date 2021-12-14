from rest_framework import viewsets
from .serializers import CommentSerializer, ReviewSerializer
from reviews.models import Titles, Review
from django.shortcuts import get_object_or_404


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        titles_id = self.kwargs.get('titles_id')
        titles = get_object_or_404(Titles, id=titles_id)
        serializer.save(author=self.request.user, titles=titles)

    def get_queryset(self):
        titles_id = self.kwargs.get('titles_id')
        titles = get_object_or_404(Titles, id=titles_id)
        return titles.comments.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    # permission_classes = (
    #     permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()
