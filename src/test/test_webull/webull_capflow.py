from webull import webull
from webull.endpoints import urls

from src.test.test_webull.tsxstocks import TSX_STOCKS

wb_urls = urls()
wb = webull()


def find_ticker_id(ticker_symbol: str, region_id: int = 3):
    # wb_urls.stock_id(ticker_symbol, region_id)

    wb._region_code = region_id
    ticker_id = wb.get_ticker(ticker_symbol)
    return ticker_id


def get_capital_flows(ticker_symbol: str, region_id: int = 3):
    wb._region_code = region_id
    capital_flow = wb.get_capital_flow(ticker_symbol)

    return capital_flow


if __name__ == '__main__':

    tsx_stocks = TSX_STOCKS

    # print(tsx_stocks)

    ca_stock_dict = dict()
    for each in tsx_stocks:
        yf_symbol = each['Symbol']
        webull_symbol = str(yf_symbol).split('.')[0]
        ca_stock_dict[webull_symbol] = {'yf_symbol': yf_symbol,
                                        'name': each['Name'],
                                        'price': each['Price'],
                                        'market_cap': each['Market Cap'],
                                        'region_code': 'CA',
                                        'volume': each['Volume']}

    # print(stock_dict)

    # ca_ticker_symbol = 'CGX'
    good_tickers = ['MBIO', 'SNCR', 'KALA', 'SYRS', 'BCEL', 'CSPR', 'ADVM', 'FGNA', 'LLNW', 'GPX', 'CVM', 'SB', 'DSX',
                    'ATHA', 'ALTO', 'CTMX', 'PRVB', 'TXMD', 'AUTL', 'AHT', 'CLSK', 'UEC', 'QTT', 'ESPR', 'YQ', 'AKBA',
                    'TGB', 'MUX', 'BW', 'RSI', 'KPTI', 'PLAB', 'GTHX', 'SDC', 'GEO', 'SFL', 'ENDP', 'GATO', 'POWW',
                    'XL', 'OCUL', 'IMVT', 'STNG', 'KOS', 'DVAX', 'CENX', 'AXL', 'PBF', 'HRTX', 'SGH', 'IAG', 'AUPH',
                    'CVI', 'FSM', 'PBI', 'EB', 'IRTC', 'HYLN', 'ERF', 'DOYU', 'AMRN', 'NNDM', 'EURN', 'LX', 'PVG',
                    'EGO', 'HBM', 'ARRY', 'BLUE', 'SBLK', 'CNK', 'EQX', 'VYGV.F', 'CDE', 'BGCP', 'AVYA', 'FLGT', 'FLR',
                    'CPG', 'YALA', 'BLMN', 'OPK', 'FOLD', 'FBP', 'HIMX', 'MLHR', 'ONB', 'CRSR', 'SLQT', 'CNX', 'EAF',
                    'SAVE', 'TROX', 'GOTU', 'VIRT', 'ISBC', 'DAN', 'SSRM', 'SABR', 'FUBO', 'HUYA', 'FNB', 'GT', 'AUY',
                    'RDN', 'BTG', 'SONO', 'QFIN', 'ZIM', 'MPLN', 'MTG', 'NRZ', 'HFC', 'SBS', 'YY', 'JBLU', 'DQ',
                    'QRTE.A', 'NYCB', 'GPK', 'EXEL', 'WOOF', 'EQT', 'NOV', 'LPX', 'BMBL', 'HUN', 'ANGI', 'PAAS', 'EDR',
                    'WISH', 'X', 'HBI', 'AA', 'AXTA', 'APA', 'ALK', 'MBT', 'OVV', 'OGN', 'IIVI', 'PAA', 'FNMA', 'USFD',
                    'KGC', 'KSS', 'JEF', 'FLEX', 'GFI', 'AEG', 'BLDR', 'NLSN', 'FHN', 'VST', 'GGB', 'PLTK', 'TEVA',
                    'MRO', 'IQ', 'CF', 'DAR', 'PENN', 'TPR', 'RLX', 'CLF', 'ZNGA', 'EDU', 'CX', 'MOS', 'SOFI', 'SBSW',
                    'SID', 'NVAX', 'VIPS', 'PHM', 'WRK', 'VIV', 'CCK', 'LBTY.A', 'LBTY.K', 'TAL', 'ACGL', 'ENIA',
                    'ATUS', 'FANG', 'BKR', 'VTRS', 'HPE', 'DVN', 'CVE', 'TTWO', 'DISC.K', 'DISC.A', 'GRUB', 'FOX',
                    'TCOM', 'WDC', 'HBAN', 'TME', 'CNHI', 'DLTR', 'LU', 'UMC', 'CS', 'DAL', 'ET', 'WY', 'LUV', 'CTVA',
                    'DHI', 'MT', 'CSGP', 'SU', 'GLW', 'CTSH', 'MPC', 'GOLD', 'PXD', 'CNQ', 'BBVA', 'PHG', 'ERIC', 'VOD',
                    'BEKE', 'SMFG', 'ING', 'FCX', 'VRTX', 'AMX', 'TAK', 'GPN', 'STLA', 'EQNR', 'BIDU', 'PBR.A', 'ATVI',
                    'DELL', 'FISV', 'FDX', 'COP', 'CI', 'GM', 'MU', 'BTI', 'HSBC', 'TTE', 'LFC', 'JD', 'BUD', 'C',
                    'RDS.B', 'RDS.A', 'QCOM', 'MRK', 'TCEH.Y', 'BABA']
    # for each in ca_stock_dict.keys():
    for each in good_tickers:
        try:
            ca_capital_flow = get_capital_flows(each, 6)
            superLargeNetFlow = ca_capital_flow['latest']['item']['superLargeNetFlow']
            newLargeNetFlow = ca_capital_flow['latest']['item']['newLargeNetFlow']
            if superLargeNetFlow > 100000 or newLargeNetFlow > 100000:
                print(f"{each} >> superLargeNetFlow: {ca_capital_flow['latest']['item']['superLargeNetFlow']} vs "
                      f"newLargeNetFlow: {ca_capital_flow['latest']['item']['newLargeNetFlow']}")

        except ValueError as err:
            pass

        except KeyError:
            pass
