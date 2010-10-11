from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from scanner.models import News, Stock
from scanner.utils import DataFetcher

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
    profile = request.user.get_profile()
    df = DataFetcher(profile)
    try:
        df.fetch_all_data(tickers=symbols)
    finally:
        df.destroy()
    # TODO: sucks that we have to fetch twice, but need to make
    # sure we pick up updates from above fetches
    stocks = get_or_create_stocks(symbols)

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

# vim: set ts=4 sw=4 et:
