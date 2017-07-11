# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

# Create your views here.

# def index(request):
#   latest_question_list = Question.objects.order_by('-pub_date')[:5]
#   context = { 'latest_question_list': latest_question_list }
#   return render(request, 'polls/index.html', context)

# def detail(request, question_id):
#   question = get_object_or_404(Question, pk=question_id)
#   return render(request, 'polls/detail.html', {'question': question})

# def results(request, question_id):
#   question = get_object_or_404(Question, pk=question_id)
#   return render(request, 'polls/results.html', {'question': question})

# GENERIC VIEWS

class IndexView(generic.ListView):
  template_name = 'polls/index.html'
  context_object_name = 'latest_question_list'

  def get_queryset(self):
    """
    For admin -> Return the last five published questions
    For the rest of the users -> Return the last five published questions (not including those to be
    published in the future)
    """
    if isAdmin(self):
      return Question.objects.order_by('-pub_date')[:5]
    else :
      return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
  model = Question
  template_name = 'polls/detail.html'

  def get_queryset(self):
    # include future questions only for admins
    if isAdmin(self):
      return Question.objects.all()
    else :
      return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
  model = Question
  template_name = 'polls/results.html'

  def get_queryset(self):
    # include future questions only for admins
    if isAdmin(self):
      return Question.objects.all()
    else :
      return Question.objects.filter(pub_date__lte=timezone.now())


def vote(request, question_id):
  p = get_object_or_404(Question, pk=question_id)
  try:
    selected_choice = p.choice_set.get(pk=request.POST['choice'])
  except (KeyError, Choice.DoesNotExist):
    # Redisplay the question voting form.
    return render(request, 'polls/detail.html', {
      'question': p,
      'error_message': "You didn't select a choice.",
      })
  else:
    selected_choice.votes += 1
    selected_choice.save()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.

    return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
  return HttpResponse("You're voting on question %s." % question_id)


def isAdmin(request):
  return request.request.user.is_authenticated() and request.request.user.is_superuser