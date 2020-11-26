#!/usr/bin/python3
# -*- coding: utf-8

#  Monitoring monitoring-utils
#
#  Monitoring monitoring-utils are the background magic for my plugins, scripts and more
#
#  Copyright (c) 2020 Fabian Fröhlich <mail@confgen.org> <https://icinga2.confgen.org>
#
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  For all license terms see README.md and LICENSE Files in root directory of this Project.
#
#  Checkout this project on github <https://github.com/f-froehlich/monitoring-utils>
#  and also my other projects <https://github.com/f-froehlich>


import dns.resolver


class DNSExecutor:

    def __init__(self, logger, parser, status_builder, nameservers):

        self.__nameservers = nameservers
        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser

        self.__resolver = dns.resolver.Resolver()
        self.__resolver.use_edns(0, dns.flags.DO, 4096)
        self.__resolver.nameservers = ([nameservers])

    def resolve(self, domain, rdtype, save_status=True):

        record_name = self.get_record_for_type(rdtype)
        try:
            self.__logger.info('Resolve ' + record_name + ' record for domain "' + domain + '"')
            domain_name = dns.name.from_text(domain)
            response = self.__resolver.query(domain_name, rdtype, dns.rdataclass.IN, True).response
            for record in response.answer:
                self.__logger.debug('Found ' + record_name + ' record "' + str(record) + '"')
            return response
        except dns.resolver.NoAnswer:
            # No answer found -> record not exist
            self.__logger.info('No ' + record_name + ' record found for domain "' + domain + '"')
            if save_status:
                self.__status_builder.unknown('No ' + record_name + ' record found for domain "' + domain + '"')

        except dns.resolver.NXDOMAIN:
            # Domain not exist
            self.__logger.info('Got NXDOMAIN for domain "' + domain + '"')
            if save_status:
                self.__status_builder.unknown('Got NXDOMAIN for domain "' + domain + '"')

        return None

    def get_record_for_type(self, rdtype):

        types = {
            dns.rdatatype.A: 'A',
            dns.rdatatype.AAAA: 'AAAA',
            dns.rdatatype.ANY: 'ANY',
            dns.rdatatype.CNAME: 'CNAME',
            dns.rdatatype.MX: 'MX',
            dns.rdatatype.NS: 'NS',
            dns.rdatatype.PTR: 'PTR',
            dns.rdatatype.SRV: 'SRV',
            dns.rdatatype.TXT: 'TXT',
            dns.rdatatype.DNSKEY: 'DNSKEY',
            dns.rdatatype.RRSIG: 'RRSIG',
            dns.rdatatype.SOA: 'SOA',
        }
        return types.get(rdtype, str(rdtype))

    def resolve_A(self, domain, save_status=True):
        return self.resolve(domain, dns.rdatatype.A, save_status)

    def resolve_AAAA(self, domain, save_status=True):
        return self.resolve(domain, dns.rdatatype.AAAA, save_status)

    def resolve_SOA(self, domain, save_status=True):
        return self.resolve(domain, dns.rdatatype.SOA, save_status)

    def resolve_CNAME(self, domain, save_status=True):
        return self.resolve(domain, dns.rdatatype.CNAME, save_status)

    def resolve_TXT(self, domain, save_status=True):
        return self.resolve(domain, dns.rdatatype.TXT, save_status)

    def resolve_SPF(self, domain, save_status=True):
        txt = None
        soa = self.resolve_SOA(domain, False)
        zone = '.'.join(domain.split('.')[1::])
        if None == soa:
            self.__logger.info('No SOA record found for domain "' + domain + '". Fetching SPF from Zone "' + zone
                               + '" instead')
            txt = self.resolve_TXT(zone, False)
        else:
            self.__logger.info('Found SOA record found for zone "' + domain + '".')
            txt = self.resolve_TXT(domain, False)

        if None == txt:
            self.__logger.info('No TXT record found')
            if save_status:
                if None == soa:
                    self.__status_builder.unknown('No SPF record found for zone "' + zone + '"')
                else:
                    self.__status_builder.unknown('No SPF record found for domain "' + domain + '"')

            return None

        spf = []
        # search for SPF record
        for record in txt.answer:
            record = record.to_text()
            self.__logger.debug('Search SPF policy in TXT record "' + record + '".')
            if 'TXT' in record and '"v=spf1' not in record:
                continue

            record_array = record.split('"v=spf1')
            if len(record_array) >= 2:
                value = record_array[1]
                value = value.replace('v=spf1', '')
                value = value.replace('"', '')
                value = value.strip()

                if value not in spf:
                    self.__logger.debug('Found SPF policy "' + value + '".')
                    spf.append(value)

        return spf

    def resolve_DNSKEY(self, domain, save_status=True):
        return self.resolve(domain, dns.rdatatype.DNSKEY, save_status)

    def resolve_RRSIG(self, domain, save_status=True, recursion=False):

        response = self.resolve_DNSKEY(domain, False)

        if None == response:
            soa = self.resolve_SOA(domain, False)

            if not recursion and None == soa:
                # domain is not a zone -> search for DNSKEY in zone instead
                zone = '.'.join(domain.split('.')[1::])
                self.__logger.info(
                    'Domain "' + domain + '" is not a zone, resolve DNSKEY from zone "' + zone + '" instead.')

                response = self.resolve_RRSIG(zone, save_status, True)
                if None != response:
                    return response

                # parent zone not signed -> domain can't be signed
                self.__logger.debug('Zone "' + zone + '" seams not to be signed with DNSSEC, therefore domain "'
                                    + domain + '" can\'t be signed')
                self.__logger.info('Domain "' + domain + '" seams not to be signed with DNSSEC')

                if save_status:
                    self.__status_builder.unknown(
                        'Domain "' + domain + '" seams not to be signed with DNSSEC')

            elif not recursion:
                # No DNSKEY found
                self.__logger.info('Domain "' + domain + '" seams not to be signed with DNSSEC')
                if save_status:
                    self.__status_builder.unknown(
                        'Domain "' + domain + '" seams not to be signed with DNSSEC')

            return None

        try:
            # if domain is CNAME search for target domain and get RRSIG of it instead
            cname_domain = None
            while True:
                cname = self.resolve_CNAME(domain if None == cname_domain else cname_domain, save_status=False)
                if None == cname:
                    break
                for a in cname.answer:
                    record = a.to_text().split()
                    if len(record) >= 5 and record[3] == "CNAME":
                        cname_domain = record[4]
                        break

            domain_name = dns.name.from_text(domain if None == cname_domain else cname_domain)
            # search for RRSET
            rrsig = response.find_rrset(response.answer, domain_name, dns.rdataclass.IN, dns.rdatatype.RRSIG,
                                        dns.rdatatype.DNSKEY)
            if 0 == len(rrsig):
                self.__logger.info(
                    'No RRSIG found for domain "' + domain + '" but zone seams to be signed with DNSSEC.')
                if save_status:
                    self.__status_builder.critical(
                        'No RRSIG found for domain "' + domain + '" but zone seams to be signed with DNSSEC.')
                return None

            for record in rrsig:
                self.__logger.debug('Found matching RRSIG record "' + str(record) + '"')

            return rrsig
        except KeyError:
            self.__logger.info('No matching RRSIG found for domain "' + domain + '" but DNSKEY exists.')
            if save_status:
                self.__status_builder.critical('No matching RRSIG found for domain "' + domain + '" but DNSKEY exists.')
