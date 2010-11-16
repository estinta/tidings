from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from scanner.models import News, Stock
from scanner.utils import DataFetcher

from .forms import CheckupForm, BuildListForm, process_build_list

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

def checkup_get_defaults(user, checkup_data):
    df = DataFetcher(user.get_profile())
    symbols = [d['ticker'] for d in checkup_data]
    try:
        # TODO don't need any news
        df.fetch_all_data(tickers=symbols)
    finally:
        df.destroy()

    mapper = {
            'sector_rank': 'ibd_industry_rank',
            'eps': 'ibd_earnings_percentage_lastquarter',
            'eps_rank': 'ibd_eps_rank',
            'sales_percentage': 'ibd_sales_percentage_lastquarter',
            'total_float': 'finviz_float',
    }

    for item in checkup_data:
        try:
            stock = Stock.objects.get(ticker=item['ticker'])
        except Stock.DoesNotExist:
            continue
        for field, value in mapper.iteritems():
            if field not in item or not item[field]:
                item[field] = getattr(stock, value)

@login_required
def checkup(request):
    CheckupFormSet = formset_factory(CheckupForm, extra=3, can_delete=True)
    valid_data = []

    if request.method == 'POST':
        formset = CheckupFormSet(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                if form not in formset.deleted_forms:
                    if 'ticker' in form.cleaned_data:
                        valid_data.append(form.cleaned_data)
            checkup_get_defaults(request.user, valid_data)
            formset = CheckupFormSet(initial=valid_data)
    else:
        # first time on page, grab the usual list in the session
        symbols = request.session.get('symbols', set())
        valid_data = [{'ticker': s} for s in symbols]
        checkup_get_defaults(request.user, valid_data)
        formset = CheckupFormSet(initial=valid_data)

    ctx = RequestContext(request, {
        "stock_formset": formset,
        "valid_data": valid_data,
    })
    return render_to_response("reporter/checkup.html", ctx)

# vim: set ts=4 sw=4 et:
