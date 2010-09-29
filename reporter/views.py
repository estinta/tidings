from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from scanner.models import News, Stock
from scanner.utils import fetch_ibd, fetch_finviz, fetch_news

from .forms import BuildListForm, process_build_list

def get_or_create_stocks(symbols):
    stocks = []
    for symbol in symbols:
        stock, created = Stock.objects.get_or_create(ticker=symbol)
        stocks.append(stock)
    return stocks

@login_required
def index(request):
    build_list_form = BuildListForm()
    symbols = process_build_list(request)
    stocks = get_or_create_stocks(symbols)
    fetch_news(user=request.user, tickers=symbols)
    profile = request.user.get_profile()
    fetch_ibd(profile.ibd_user, profile.ibd_password,
            user=request.user, tickers=symbols)
    fetch_finviz(user=request.user, tickers=symbols)
    # TODO: sucks that we have to fetch twice, but need to make
    # sure we pick up updates from above fetches
    stocks = get_or_create_stocks(request.user, symbols)

    ctx = RequestContext(request, {
        'build_list_form': build_list_form,
        'stocks': stocks,
    })
    return render_to_response('reporter/index.html', ctx)

@login_required
def remove_symbol(request, symbol):
    symbols = request.session.get('symbols', set())
    symbols.discard(symbol)
    request.session['symbols'] = symbols
    return redirect('/')

@login_required
def remove_all_symbols(request):
    request.session['symbols'] = set()
    return redirect('/')

# TODO: admin only, perhaps?
@login_required
def purge_db(request):
    Stock.objects.all().delete()
    return redirect('/')

# vim: set ts=4 sw=4 et:
