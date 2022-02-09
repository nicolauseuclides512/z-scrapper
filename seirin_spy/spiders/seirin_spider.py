import scrapy
from time import sleep
from random import randint
import requests
import json
import os
import subprocess


class SeirinSpider(scrapy.Spider):
    name = "kuroko"
    # rotate_user_agent = True

    def start_requests(self):
        for i in range(10238281, 10238781):
            url = ('https://www.tokopedia.com/people/{}'.format(i))
            yield scrapy.Request(url=url, callback=self.parse)
            if i % 4000 == 0:
                sleep(randint(5, 10))

    def parse(self, response):
        user_content = response.css('div.user-content').extract_first()
        if user_content.find('user-has-shop') != -1:
            link_toko = response.css('div.span5 a::attr(href)').extract_first()
            link_info = '{}/info'.format(link_toko)
            yield response.follow(link_info, self.parse_toko)

    def parse_toko(self, response):
        try:
            # data awal yang dikumpulkan untuk penentuan toko aktif atau tidak
            id_pemilik = response.css('div.shop-owner-wrapper a::attr(href)').extract_first().strip(
                'https://www.tokopedia.com/people/')
            nick_toko = response.request.url.replace('https://www.tokopedia.com/', '').replace('/info', '')
            status_toko = response.css('a.shop-logo-url').extract_first()
            membership = "-"
            # menentukan apakah toko aktif atau tidak
            if status_toko.find('Status Toko') != -1:  # toko tidak aktif
                # mengumpulkan data general baik gold maupun green
                # set status_toko
                status_toko = 'Toko Tidak Aktif'
                # nama_pemilik
                nama_pemilik = response.css('div.shop-owner-wrapper a::text').extract_first().strip()
                # mengambil info ada foto toko
                loc_toko = response.css('ul.shop-info-location::text').extract_first().strip()
                # masuk ke folder image
                os.chdir('image')
                if loc_toko != 'Belum ada lokasi toko':  # toko punya lokasi toko
                    # mengambil semua alamat toko
                    alamat = response.css('ul.shop-info-location p::text').extract()
                    alamat = [s.strip() for s in alamat]
                    # mengambil semua contact toko
                    contact = response.css('ul.shop-info-location img::attr(src)').extract()
                    contact = [s.strip() for s in contact]
                    # memeriksa apakah folder dengan nama nick_toko sudah ada
                    if os.path.exists('{}'.format(nick_toko)):  # folder sudah ada
                        # masuk ke folder dengan nama nick_toko
                        os.chdir('{}'.format(nick_toko))
                        # loop di semua contact
                        for key in range(0, len(contact)):
                            # mendownload semua gambar contact
                            subprocess.call(['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P',
                                             '{}'.format(nick_toko)])
                        # kembali ke folder image
                        os.chdir('..')
                        # kembali ke folder spiders
                        os.chdir('..')
                    else:  # folder belum ada
                        # membuat folder dengan nama nick_toko
                        subprocess.call('mkdir {}'.format(nick_toko), shell=True)
                        # mengubah hak akses folder nick_toko
                        subprocess.call('chmod 777 {}'.format(nick_toko), shell=True)
                        # masuk ke folder dengan nama nick_toko
                        os.chdir('{}'.format(nick_toko))
                        # loop di semua contact
                        for key in range(0, len(contact)):
                            # mendownload semua gambar contact
                            subprocess.call(['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P',
                                             '{}'.format(nick_toko)])
                        # kembali ke folder image
                        os.chdir('..')
                        # kembali ke folder spiders
                        os.chdir('..')

                        # memasukkan data toko tidak aktif yang memiliki lokasi
                    yield {
                        'id_pemilik': id_pemilik,
                        'nick_toko': nick_toko,
                        'status_toko': status_toko,
                        'nama_toko': '-',
                        'nama_pemilik': nama_pemilik,
                        'reputasi': '-',
                        'transaksi_sukses': '-',
                        'produk_terjual': '-',
                        'total_showcase': '-',
                        'total_produk': '-',
                        'jumlah_favorit': '-',
                        'penjualan_1_bulan': '-',
                        'penjualan_3_bulan': '-',
                        'penjualan_12_bulan': '-',
                        'motto': '-',
                        'slogan': '-',
                        'alamat': alamat,
                        'foto_toko': '-',
                        'contact': contact,
                        'membership': membership,
                    }

                else:  # toko tidak memiliki lokasi toko
                    # kembali ke folder spiders
                    os.chdir('..')
                    # memasukkan data toko tidak aktif yang tidak memiliki lokasi
                    yield {
                        'id_pemilik': id_pemilik,
                        'nick_toko': nick_toko,
                        'status_toko': status_toko,
                        'nama_toko': '-',
                        'nama_pemilik': '-',
                        'reputasi': '-',
                        'transaksi_sukses': '-',
                        'produk_terjual': '-',
                        'total_showcase': '-',
                        'total_produk': '-',
                        'jumlah_favorit': '-',
                        'penjualan_1_bulan': '-',
                        'penjualan_3_bulan': '-',
                        'penjualan_12_bulan': '-',
                        'motto': '-',
                        'slogan': '-',
                        'alamat': '-',
                        'foto_toko': '-',
                        'contact': '-',
                        'membership': '-',
                    }

            else:  # toko aktif
                # mengumpulkan data general baik gold maupun green
                # set status_toko
                status_toko = 'Toko Aktif'
                # id_toko
                id_toko = response.xpath('//input[@name="shop_id"]/@value').extract_first().strip()
                # nama_pemilik
                nama_pemilik = response.css('div.shop-owner-wrapper a::text').extract_first().strip()
                # banyak transaksi sukses
                transaksi_sukses = response.xpath('//div[@class="row-fluid shop-statistics"]//strong/text()').extract()[
                    0].strip().replace('.', '')
                # banyak produk yang sudah trerjual
                produk_terjual = response.xpath('//div[@class="row-fluid shop-statistics"]//strong/text()').extract()[
                    1].strip().replace('.', '')
                #  banyak etalase
                total_showcase = response.xpath('//div[@class="row-fluid shop-statistics"]//strong/text()').extract()[
                    2].strip().replace('.', '')
                # banyak produk yang dijual
                total_produk = response.xpath('//div[@class="row-fluid shop-statistics"]//strong/text()').extract()[
                    3].strip().replace('.', '')

                # besar reputasi toko
                temp_reputasi = requests.get(
                    'https://www.tokopedia.com/reputationapp/reputation/api/v1/shop/{}'.format(id_toko))
                reputasi = temp_reputasi.json()['data']['shop_score'].replace('.', '')

                # banyak penjualan dalam 1 bln, 3 bln, dan 12 bln
                temp_penjualan = requests.post('https://www.tokopedia.com/ajax/shop/shop-charts.pl',
                                               data={'action': 'get_shop_tx_stats', 'shop_id': id_toko})
                html = json.loads(temp_penjualan.text)
                selector = scrapy.Selector(text=html['html'], type="html")
                penjualan = selector.xpath('//div[@class="chart-description"]//p[@class="muted fs-12"]/text()')
                if len(penjualan) == 3:  # toko memiliki penjualan dalam 1 bln, 3 bln, dan 12 bln
                    penjualan_1_bulan = \
                    selector.xpath('//div[@class="chart-description"]//p[@class="muted fs-12"]/text()').extract()[
                        0].strip('Dari Transaksi').replace('.', '')
                    penjualan_3_bulan = \
                    selector.xpath('//div[@class="chart-description"]//p[@class="muted fs-12"]/text()').extract()[
                        1].strip('Dari Transaksi').replace('.', '')
                    penjualan_12_bulan = \
                    selector.xpath('//div[@class="chart-description"]//p[@class="muted fs-12"]/text()').extract()[
                        2].strip('Dari Transaksi').replace('.', '')
                elif len(penjualan) == 2:  # toko memiliki penjualan dalam 3 bln, dan 12 bln
                    penjualan_1_bulan = 'Belum ada Transaksi'
                    penjualan_3_bulan = \
                    selector.xpath('//div[@class="chart-description"]//p[@class="muted fs-12"]/text()').extract()[
                        0].strip('Dari Transaksi').replace('.', '')
                    penjualan_12_bulan = \
                    selector.xpath('//div[@class="chart-description"]//p[@class="muted fs-12"]/text()').extract()[
                        1].strip('Dari Transaksi').replace('.', '')
                elif len(penjualan) == 1:  # toko memiliki penjualan dalam 12 bln
                    penjualan_1_bulan = 'Belum ada Transaksi'
                    penjualan_3_bulan = 'Belum ada Transaksi'
                    penjualan_12_bulan = \
                    selector.xpath('//div[@class="chart-description"]//p[@class="muted fs-12"]/text()').extract()[
                        0].strip('Dari Transaksi').replace('.', '')
                else:  # toko tidak memiliki penjualan dalam 1 bln, 3 bln, dan 12 bln
                    penjualan_1_bulan = 'Belum ada Transaksi'
                    penjualan_3_bulan = 'Belum ada Transaksi'
                    penjualan_12_bulan = 'Belum ada Transaksi'

                # mengambil link foto toko
                foto_toko = response.css('a.shop-logo-url img::attr(src)').extract_first()
                # mengambil info ada foto toko
                loc_toko = response.css('ul.shop-info-location::text').extract_first().strip()
                # mengambil info untuk gold atau green
                gold = response.xpath('//div[@class="row-fluid shop-header"]//div/@class').extract_first()

                # memeriksa apakah gold atau green
                if gold.find('gold') != -1:  # gold merchant
                    # mengambil data gold merchant
                    membership = 'gold'
                    # nama toko
                    nama_toko = response.xpath('//h1[@itemprop="name"]/text()').extract_first().strip()
                    # slogan
                    slogan = response.css('div.shop-slogan::text').extract()[1].strip()
                    # motto
                    motto = response.css('div.slogan small::text').extract_first()
                    # jumlah favorit
                    jumlah_favorit = response.css('li.favorite-wrapper b::text').extract_first().strip().replace('.',
                                                                                                                 '')
                    # masuk ke folder image
                    os.chdir('image')

                    # memeriksa apakah ada foto_toko
                    if foto_toko == 'https://imagerouter.tokopedia.com/img/215-square/default_v3-shopnophoto.png':  # toko belum ada foto
                        foto_toko = 'Belum ada foto toko'
                    else:  # toko ada foto
                        foto_toko = foto_toko
                        # membuat folder dengan nama nick_toko
                        subprocess.call('mkdir {}'.format(nick_toko), shell=True)
                        # mengubah hak akses folder nick_toko
                        subprocess.call('chmod 777 {}'.format(nick_toko), shell=True)
                        # masuk ke folder dengan nama nick_toko
                        os.chdir('{}'.format(nick_toko))
                        # mendownload gambar foto toko
                        subprocess.call(['wget', '-O {}_{}.png'.format(nama_toko, nick_toko), foto_toko, '-P',
                                         '{}'.format(nick_toko)])
                        # kembali ke folder image
                        os.chdir('..')

                    # memeriksa apakah toko memiliki lokasi toko
                    if loc_toko != 'Belum ada lokasi toko':  # toko punya lokasi toko
                        # mengambil semua alamat toko
                        alamat = response.css('ul.shop-info-location p::text').extract()
                        alamat = [s.strip() for s in alamat]
                        # mengambil semua contact toko
                        contact = response.css('ul.shop-info-location img::attr(src)').extract()
                        contact = [s.strip() for s in contact]
                        # memeriksa apakah folder dengan nama nick_toko sudah ada
                        if os.path.exists('{}'.format(nick_toko)):  # folder sudah ada
                            # masuk ke folder dengan nama nick_toko
                            os.chdir('{}'.format(nick_toko))
                            # loop di semua contact
                            for key in range(0, len(contact)):
                                # mendownload semua gambar contact
                                subprocess.call(['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P',
                                                 '{}'.format(nick_toko)])
                            # kembali ke folder image
                            os.chdir('..')
                            # kembali ke folder spiders
                            os.chdir('..')
                        else:
                            # membuat folder dengan nama nick_toko
                            subprocess.call('mkdir {}'.format(nick_toko), shell=True)
                            # mengubah hak akses folder nick_toko
                            subprocess.call('chmod 777 {}'.format(nick_toko), shell=True)
                            # masuk ke folder dengan nama nick_toko
                            os.chdir('{}'.format(nick_toko))
                            # loop di semua contact
                            for key in range(0, len(contact)):
                                # mendownload semua gambar contact
                                subprocess.call(['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P',
                                                 '{}'.format(nick_toko)])
                            # kembali ke folder image
                            os.chdir('..')
                            # kembali ke folder spiders
                            os.chdir('..')

                        # memasukkan data gold merchant yang memiliki info lokasi toko
                        yield {
                            'id_pemilik': id_pemilik,
                            'nick_toko': nick_toko,
                            'status_toko': status_toko,
                            'nama_toko': nama_toko,
                            'nama_pemilik': nama_pemilik,
                            'reputasi': reputasi,
                            'transaksi_sukses': transaksi_sukses,
                            'produk_terjual': produk_terjual,
                            'total_showcase': total_showcase,
                            'total_produk': total_produk,
                            'jumlah_favorit': jumlah_favorit,
                            'penjualan_1_bulan': penjualan_1_bulan,
                            'penjualan_3_bulan': penjualan_3_bulan,
                            'penjualan_12_bulan': penjualan_12_bulan,
                            'motto': motto,
                            'slogan': slogan,
                            'alamat': alamat,
                            'foto_toko': foto_toko,
                            'contact': contact,
                            'membership': membership,
                        }

                    else:  # toko tidak memiliki lokasi toko
                        # kembali ke folder spiders
                        os.chdir('..')
                        # memasukkan data gold merchant yang tidak memiliki info lokasi toko
                        yield {
                            'id_pemilik': id_pemilik,
                            'nick_toko': nick_toko,
                            'status_toko': status_toko,
                            'nama_toko': nama_toko,
                            'nama_pemilik': nama_pemilik,
                            'reputasi': reputasi,
                            'transaksi_sukses': transaksi_sukses,
                            'produk_terjual': produk_terjual,
                            'total_showcase': total_showcase,
                            'total_produk': total_produk,
                            'jumlah_favorit': jumlah_favorit,
                            'penjualan_1_bulan': penjualan_1_bulan,
                            'penjualan_3_bulan': penjualan_3_bulan,
                            'penjualan_12_bulan': penjualan_12_bulan,
                            'motto': motto,
                            'slogan': slogan,
                            'alamat': '-',
                            'foto_toko': foto_toko,
                            'contact': '-',
                            'membership': membership,
                        }

                else:  # green merchant
                    # mengambil data green merchant
                    # nama_toko
                    membership = 'green'
                    nama_toko = response.xpath('//span[@itemprop="name"]/text()').extract_first().strip()
                    # motto
                    motto = response.xpath('//div[@class="span10"]/div/text()').extract()[3].strip()
                    # slogan
                    slogan = response.css('p.shop-slogan::text').extract_first().strip()
                    # jumlah favorit
                    jumlah_favorit = response.css('li.favorite-wrapper strong::text').extract_first().strip().replace(
                        '.', '')
                    # masuk ke folder image
                    os.chdir('image')

                    # memeriksa apakah ada foto_toko
                    if foto_toko == 'https://imagerouter.tokopedia.com/img/215-square/default_v3-shopnophoto.png':  # toko belum ada foto
                        foto_toko = 'Belum ada foto toko'
                    else:  # toko ada foto
                        foto_toko = foto_toko
                        # membuat folder dengan nama nick_toko
                        subprocess.call('mkdir {}'.format(nick_toko), shell=True)
                        # mengubah hak akses folder nick_toko
                        subprocess.call('chmod 777 {}'.format(nick_toko), shell=True)
                        # masuk ke folder dengan nama nick_toko
                        os.chdir('{}'.format(nick_toko))
                        # mendownload gambar foto toko
                        subprocess.call(['wget', '-O {}_{}.png'.format(nama_toko, nick_toko), foto_toko, '-P',
                                         '{}'.format(nick_toko)])
                        # kembali ke folder image
                        os.chdir('..')

                    # memeriksa apakah toko memiliki lokasi toko
                    if loc_toko != 'Belum ada lokasi toko':  # toko punya lokasi toko
                        # mengambil semua alamat toko
                        alamat = response.css('ul.shop-info-location p::text').extract()
                        alamat = [s.strip() for s in alamat]
                        # mengambil semua contact toko
                        contact = response.css('ul.shop-info-location img::attr(src)').extract()
                        contact = [s.strip() for s in contact]
                        # memeriksa apakah folder dengan nama nick_toko sudah ada
                        if os.path.exists('{}'.format(nick_toko)):  # folder sudah ada
                            # masuk ke folder dengan nama nick_toko
                            os.chdir('{}'.format(nick_toko))
                            # loop di semua contact
                            for key in range(0, len(contact)):
                                # mendownload semua gambar contact
                                subprocess.call(['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P',
                                                 '{}'.format(nick_toko)])
                            # kembali ke folder image
                            os.chdir('..')
                            # kembali ke folder spiders
                            os.chdir('..')
                        else:
                            # membuat folder dengan nama nick_toko
                            subprocess.call('mkdir {}'.format(nick_toko), shell=True)
                            # mengubah hak akses folder nick_toko
                            subprocess.call('chmod 777 {}'.format(nick_toko), shell=True)
                            # masuk ke folder dengan nama nick_toko
                            os.chdir('{}'.format(nick_toko))
                            # loop di semua contact
                            for key in range(0, len(contact)):
                                # mendownload semua gambar contact
                                subprocess.call(['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P',
                                                 '{}'.format(nick_toko)])
                            # kembali ke folder image
                            os.chdir('..')
                            # kembali ke folder spiders
                            os.chdir('..')

                        # memasukkan data gold merchant yang memiliki info lokasi toko
                        yield {
                            'id_pemilik': id_pemilik,
                            'nick_toko': nick_toko,
                            'status_toko': status_toko,
                            'nama_toko': nama_toko,
                            'nama_pemilik': nama_pemilik,
                            'reputasi': reputasi,
                            'transaksi_sukses': transaksi_sukses,
                            'produk_terjual': produk_terjual,
                            'total_showcase': total_showcase,
                            'total_produk': total_produk,
                            'jumlah_favorit': jumlah_favorit,
                            'penjualan_1_bulan': penjualan_1_bulan,
                            'penjualan_3_bulan': penjualan_3_bulan,
                            'penjualan_12_bulan': penjualan_12_bulan,
                            'motto': motto,
                            'slogan': slogan,
                            'alamat': alamat,
                            'foto_toko': foto_toko,
                            'contact': contact,
                            'membership': membership,
                        }

                    else:  # toko tidak memiliki lokasi toko
                        # kembali ke folder spiders
                        os.chdir('..')
                        # memasukkan data gold merchant yang tidak memiliki info lokasi toko
                        yield {
                            'id_pemilik': id_pemilik,
                            'nick_toko': nick_toko,
                            'status_toko': status_toko,
                            'nama_toko': nama_toko,
                            'nama_pemilik': nama_pemilik,
                            'reputasi': reputasi,
                            'transaksi_sukses': transaksi_sukses,
                            'produk_terjual': produk_terjual,
                            'total_showcase': total_showcase,
                            'total_produk': total_produk,
                            'jumlah_favorit': jumlah_favorit,
                            'penjualan_1_bulan': penjualan_1_bulan,
                            'penjualan_3_bulan': penjualan_3_bulan,
                            'penjualan_12_bulan': penjualan_12_bulan,
                            'motto': motto,
                            'slogan': slogan,
                            'alamat': '-',
                            'foto_toko': foto_toko,
                            'contact': '-',
                            'membership': membership,
                        }

        except:
            id_pemilik = response.css('div.shop-owner-wrapper a::attr(href)').extract_first().strip(
                'https://www.tokopedia.com/people/')
            nick_toko = response.request.url.replace('https://www.tokopedia.com/', '').replace('/info', '')
            # set status_toko
            status_toko = 'Error'
            # memasukkan data id pemilik danb nick toko
            nama_pemilik = response.css('div.shop-owner-wrapper a::text').extract_first().strip()
            # mengambil info ada foto toko
            loc_toko = response.css('ul.shop-info-location::text').extract_first().strip()
            # masuk ke folder image
            os.chdir('image')
            if loc_toko != 'Belum ada lokasi toko':  # toko punya lokasi toko
                # mengambil semua alamat toko
                alamat = response.css('ul.shop-info-location p::text').extract()
                alamat = [s.strip() for s in alamat]
                # mengambil semua contact toko
                contact = response.css('ul.shop-info-location img::attr(src)').extract()
                contact = [s.strip() for s in contact]
                # memeriksa apakah folder dengan nama nick_toko sudah ada
                if os.path.exists('{}'.format(nick_toko)):  # folder sudah ada
                    # masuk ke folder dengan nama nick_toko
                    os.chdir('{}'.format(nick_toko))
                    # loop di semua contact
                    for key in range(0, len(contact)):
                        # mendownload semua gambar contact
                        subprocess.call(
                            ['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P', '{}'.format(nick_toko)])
                    # kembali ke folder image
                    os.chdir('..')
                    # kembali ke folder spiders
                    os.chdir('..')
                else:  # folder belum ada
                    # membuat folder dengan nama nick_toko
                    subprocess.call('mkdir {}'.format(nick_toko), shell=True)
                    # mengubah hak akses folder nick_toko
                    subprocess.call('chmod 777 {}'.format(nick_toko), shell=True)
                    # masuk ke folder dengan nama nick_toko
                    os.chdir('{}'.format(nick_toko))
                    # loop di semua contact
                    for key in range(0, len(contact)):
                        # mendownload semua gambar contact
                        subprocess.call(
                            ['wget', '-O {}_{}.png'.format(nick_toko, key), contact[key], '-P', '{}'.format(nick_toko)])
                    # kembali ke folder image
                    os.chdir('..')
                    # kembali ke folder spiders
                    os.chdir('..')

                    # memasukkan data toko tidak aktif yang memiliki lokasi
                yield {
                    'id_pemilik': id_pemilik,
                    'nick_toko': nick_toko,
                    'status_toko': status_toko,
                    'nama_toko': '-',
                    'nama_pemilik': nama_pemilik,
                    'reputasi': '-',
                    'transaksi_sukses': '-',
                    'produk_terjual': '-',
                    'total_showcase': '-',
                    'total_produk': '-',
                    'jumlah_favorit': '-',
                    'penjualan_1_bulan': '-',
                    'penjualan_3_bulan': '-',
                    'penjualan_12_bulan': '-',
                    'motto': '-',
                    'slogan': '-',
                    'alamat': alamat,
                    'foto_toko': '-',
                    'contact': contact,
                    'membership': '-',
                }
            else:  # toko tidak memiliki lokasi toko
                # kembali ke folder spiders
                os.chdir('..')
                # memasukkan data toko tidak aktif yang tidak memiliki lokasi
                yield {
                    'id_pemilik': id_pemilik,
                    'nick_toko': nick_toko,
                    'status_toko': status_toko,
                    'nama_toko': '-',
                    'nama_pemilik': '-',
                    'reputasi': '-',
                    'transaksi_sukses': '-',
                    'produk_terjual': '-',
                    'total_showcase': '-',
                    'total_produk': '-',
                    'jumlah_favorit': '-',
                    'penjualan_1_bulan': '-',
                    'penjualan_3_bulan': '-',
                    'penjualan_12_bulan': '-',
                    'motto': '-',
                    'slogan': '-',
                    'alamat': '-',
                    'foto_toko': '-',
                    'contact': '-',
                    'membership': '-',
                }