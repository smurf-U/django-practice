from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.utils import timezone
from django.views import generic
from .models import Post, Publisher, Book, Author
from .forms import PostForm


class CommentForm(forms.Form):
    name = forms.CharField(widget=forms.Textarea(attrs={'class': 'special'}))
    email = forms.EmailField(help_text='A valid email address, please.')
    url = forms.URLField()
    comment = forms.CharField()
    date = forms.DateTimeField(widget=forms.DateTimeInput())
    choice = forms.MultipleChoiceField(choices=[
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    ], widget=forms.CheckboxSelectMultiple, )
    tchoice = forms.TypedChoiceField(choices=[
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    ])
    captcha_answer = forms.IntegerField(label='2 + 2', label_suffix=' =')


# Create your views here.

class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Post.objects.all()


class DetailView(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by(
        'published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


class PublisherList(generic.ListView):
    model = Publisher
    context_object_name = 'my_favorite_publishers'


class PublisherDetail(generic.DetailView):
    model = Publisher
    context_object_name = 'publisher'
    queryset = Publisher.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublisherDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['book_list'] = Book.objects.all()
        return context


class BookList(generic.ListView):
    queryset = Book.objects.order_by('-publication_date')
    context_object_name = 'book_list'


class AcmeBookList(generic.ListView):
    context_object_name = 'book_list'
    queryset = Book.objects.filter(publisher__name='Acme Publishing')
    template_name = 'blog/acme_list.html'


class PublisherBookList(generic.ListView):
    template_name = 'blog/books_by_publisher.html'

    def get_queryset(self):
        self.publisher = get_object_or_404(Publisher,
                                           name__contains=self.args[0])
        return Book.objects.filter(publisher=self.publisher)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PublisherBookList, self).get_context_data(**kwargs)

        # Add in the publisher
        context['publisher'] = self.publisher
        return context  ## Performing Extra Work


class AuthorDetailView(DetailView):
    queryset = Author.objects.all()

    def get_object(self):
        # Call the superclass
        object = super(AuthorDetailView, self).get_object()

        # Record the last accessed date
        object.last_accessed = timezone.now()
        object.save()
        # Return the object
        return object
