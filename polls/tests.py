# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import logging

from django.utils import timezone
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Question

# Create your tests here.

# -------- MODEL TESTS ---------- #

class QuestionMethodTest(TestCase):

  def test_was_published_recently_with_future_question(self):
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    self.assertEqual(future_question.was_published_recently(), False)

  def test_was_published_recently_with_old_question(self):
    time = timezone.now() - datetime.timedelta(days=30)
    old_question = Question(pub_date=time)
    self.assertEqual(old_question.was_published_recently(), False)

  def test_was_published_recently_with_recent_question(self):
    time = timezone.now() - datetime.timedelta(hours=1)
    recent_question = Question(pub_date=time)
    self.assertEqual(recent_question.was_published_recently(), True)

# --------- HELPERS ------------#

def create_question(question_text, days):
  time = timezone.now() + datetime.timedelta(days=days)
  return Question.objects.create(question_text=question_text, pub_date=time)

def create_choice(question, choice_text):
  return question.choice_set.create(choice_text=choice_text, votes=0)


# -------- VIEW TESTS ----------#

  # ------------- INDEX

class QuestionViewTests(TestCase):

  def test_index_view_with_no_questions(self):
    # if no questions exist, an appropiate message should be displayed
    response = self.client.get(reverse('polls:index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "No polls are available.")
    self.assertQuerysetEqual(response.context['latest_question_list'], [])

  def test_index_view_with_a_past_question(self):
    # question with a pub_date in the past should be displayed on the index page
    create_question(question_text="Past question.", days=-30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
        response.context['latest_question_list'],['<Question: Past question.>']
      )

  def test_index_view_with_a_future_question(self):
    # questions with a pub_date in the future, should not be displayed on the index page
    create_question(question_text="Future question.", days=30)
    response = self.client.get(reverse('polls:index'))
    self.assertContains(response, "No polls are available.", status_code=200)
    self.assertQuerysetEqual(response.context['latest_question_list'], [])

  def test_index_view_with_future_question_and_past_question(self):
    # only past questions should be displayed
    create_question(question_text="Past question.", days=-30)
    create_question(question_text="Future question.", days=30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
        response.context['latest_question_list'],
        ['<Question: Past question.>']
      )

  def test_index_view_with_two_past_questions(self):
    # the questions index page may display multiple questions
    create_question(question_text="Past question 1.", days=-30)
    create_question(question_text="Past question 2.", days=-5)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
        response.context['latest_question_list'],
        ['<Question: Past question 2.>', '<Question: Past question 1.>']
      )

  # ------------- DETAIL

class QuestionIndexDetailTests(TestCase):

  def setUp(self):
    self.future_question = create_question(question_text='Future Question.', days=5)
    self.past_question = create_question(question_text='Past Question.', days=-5)

  def tearDown(self):
    del self.future_question
    del self.past_question

  def test_detail_view_with_a_future_question(self):
    # the detail view of a question with pub_date in the future should
    # return a 404 not found
    response = self.client.get(reverse('polls:detail', args=(self.future_question.id,)))
    self.assertEqual(response.status_code, 404)

  def test_detail_view_with_a_past_question(self):
    # the detail view of a question wiht pub_date in the past should display
    # the question's text
    response = self.client.get(reverse('polls:detail', args=(self.past_question.id,)))
    self.assertContains(response, self.past_question.question_text, status_code=200)


  # -------------- RESULTS

class QuestionResultTest(TestCase):

  def setUp(self):
    self.future_question = create_question(question_text='Future Question.', days=5)
    self.past_question = create_question(question_text='Past Question.', days=-5)

  def tearDown(self):
    del self.future_question
    del self.past_question

  def test_result_view_with_a_future_question(self):
    # the result view of a questionn with pub_date in the future should
    # return a 404 not found
    response = self.client.get(reverse('polls:results', args=(self.future_question.id,)))
    self.assertEqual(response.status_code, 404)

  def test_result_with_a_past_question_with_choices(self):
    # the result vew of a question with pub_date in the past should display
    # the question's text and it's choices
    past_choice = create_choice(question=self.past_question, choice_text='Past Choice.' )
    response = self.client.get(reverse('polls:results', args=(self.past_question.id,)))
    self.assertContains(response, self.past_question.question_text, status_code=200)
    self.assertContains(response, past_choice.choice_text)
    self.assertContains(response, past_choice.votes)

  def test_result_with_a_past_question_without_choices(self):
    # the result vew of a question with pub_date in the past and without choices
    # an appropiate message should be displayed
    response = self.client.get(reverse('polls:results', args=(self.past_question.id,)))
    self.assertContains(response, 'No choices for this question')

