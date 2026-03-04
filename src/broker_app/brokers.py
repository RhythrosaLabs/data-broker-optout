#!/usr/bin/env python3
"""
Comprehensive data broker definitions.
Based on popular opt-out lists and privacy advocacy research.
"""
from __future__ import annotations

from .models import BrokerSite

def get_comprehensive_broker_list():
    """
    Returns a comprehensive list of data broker sites
    Based on research from various privacy advocacy sources
    """
    return [
        # Popular search engines / people search
        BrokerSite(
            name="Spokeo",
            url="https://www.spokeo.com",
            opt_out_url="https://www.spokeo.com/optout",
            form_fields={
                "email": "email",
                "first_name": "fname", 
                "last_name": "lname"
            },
            instructions="Fill out email, first and last name, then verify via email",
            difficulty="easy",
            requires_verification=True
        ),
        
        BrokerSite(
            name="WhitePages",
            url="https://www.whitepages.com",
            opt_out_url="https://www.whitepages.com/suppression_requests",
            form_fields={
                "first_name": "suppression_request[first_name]",
                "last_name": "suppression_request[last_name]",
                "email": "suppression_request[email]",
                "phone": "suppression_request[phone]"
            },
            instructions="Complete form with personal details",
            difficulty="easy",
            requires_verification=False
        ),
        
        BrokerSite(
            name="BeenVerified", 
            url="https://www.beenverified.com",
            opt_out_url="https://www.beenverified.com/app/optout/search",
            form_fields={
                "first_name": "fname",
                "last_name": "lname",
                "state": "state"
            },
            instructions="Search for your profile first, then opt out",
            difficulty="medium",
            requires_verification=True
        ),
        
        BrokerSite(
            name="PeopleFinder",
            url="https://www.peoplefinder.com", 
            opt_out_url="https://www.peoplefinder.com/optout.php",
            form_fields={
                "email": "email",
                "first_name": "first_name",
                "last_name": "last_name"
            },
            instructions="Simple opt-out form",
            difficulty="easy",
            requires_verification=False
        ),
        
        BrokerSite(
            name="Intelius",
            url="https://www.intelius.com",
            opt_out_url="https://www.intelius.com/opt-out/submit/",
            form_fields={
                "first_name": "firstName",
                "last_name": "lastName", 
                "email": "email",
                "phone": "phone"
            },
            instructions="Complete opt-out form and verify email",
            difficulty="easy",
            requires_verification=True
        ),
        
        BrokerSite(
            name="TruePeopleSearch",
            url="https://www.truepeoplesearch.com",
            opt_out_url="https://www.truepeoplesearch.com/removal",
            form_fields={
                "email": "email"
            },
            instructions="Search for your listing first, then use removal form",
            difficulty="medium",
            requires_verification=True
        ),
        
        BrokerSite(
            name="FastPeopleSearch",
            url="https://www.fastpeoplesearch.com",
            opt_out_url="https://www.fastpeoplesearch.com/removal",
            form_fields={
                "email": "email"
            },
            instructions="Find your listing, then submit removal request",
            difficulty="medium", 
            requires_verification=True
        ),
        
        BrokerSite(
            name="CheckPeople",
            url="https://www.checkpeople.com",
            opt_out_url="https://www.checkpeople.com/optout",
            form_fields={
                "email": "email",
                "first_name": "first_name",
                "last_name": "last_name"
            },
            instructions="Standard opt-out form",
            difficulty="easy",
            requires_verification=False
        ),
        
        BrokerSite(
            name="USSearch",
            url="https://www.ussearch.com", 
            opt_out_url="https://www.ussearch.com/opt-out/submit/",
            form_fields={
                "first_name": "first_name",
                "last_name": "last_name",
                "email": "email"
            },
            instructions="Fill out removal request form",
            difficulty="easy",
            requires_verification=True
        ),
        
        BrokerSite(
            name="PeopleSearchNow",
            url="https://www.peoplesearchnow.com",
            opt_out_url="https://www.peoplesearchnow.com/opt-out",
            form_fields={
                "email": "email"
            },
            instructions="Search for yourself first, then opt out",
            difficulty="medium",
            requires_verification=True
        ),
        
        # Marketing/advertising data brokers
        BrokerSite(
            name="Acxiom",
            url="https://www.acxiom.com",
            opt_out_url="https://isapps.acxiom.com/optout/optout.aspx",
            form_fields={
                "first_name": "FirstName",
                "last_name": "LastName",
                "email": "Email",
                "address": "Address1",
                "city": "City",
                "state": "State",
                "zip_code": "PostalCode"
            },
            instructions="Complete comprehensive opt-out form",
            difficulty="medium",
            requires_verification=False
        ),
        
        BrokerSite(
            name="Epsilon",
            url="https://www.epsilon.com",
            opt_out_url="https://www.epsilon.com/us/privacy-policy/opt-out-form",
            form_fields={
                "first_name": "firstName",
                "last_name": "lastName", 
                "email": "email",
                "address": "address",
                "city": "city",
                "state": "state",
                "zip_code": "zipCode"
            },
            instructions="Marketing data opt-out form",
            difficulty="medium",
            requires_verification=False
        ),
        
        BrokerSite(
            name="LexisNexis", 
            url="https://www.lexisnexis.com",
            opt_out_url="https://optout.lexisnexis.com/",
            form_fields={
                "first_name": "firstName",
                "last_name": "lastName",
                "email": "email", 
                "phone": "phone",
                "address": "address",
                "city": "city",
                "state": "state",
                "zip_code": "zipCode"
            },
            instructions="Consumer reporting opt-out - requires extensive personal info",
            difficulty="hard",
            requires_verification=True
        ),
        
        # Additional brokers from research
        BrokerSite(
            name="PublicRecordsNow",
            url="https://www.publicrecordsnow.com",
            opt_out_url="https://www.publicrecordsnow.com/static/view/optout/",
            form_fields={
                "email": "email"
            },
            instructions="Email-based opt-out request",
            difficulty="easy",
            requires_verification=True
        ),
        
        BrokerSite(
            name="InstantCheckmate", 
            url="https://www.instantcheckmate.com",
            opt_out_url="https://www.instantcheckmate.com/opt-out/",
            form_fields={
                "first_name": "firstName",
                "last_name": "lastName",
                "email": "email"
            },
            instructions="Background check service opt-out",
            difficulty="easy", 
            requires_verification=True
        ),
        
        BrokerSite(
            name="MyLife",
            url="https://www.mylife.com",
            opt_out_url="https://www.mylife.com/privacy-policy",
            form_fields={
                "email": "email"
            },
            instructions="Contact via privacy policy page - manual process",
            difficulty="hard",
            requires_verification=True
        ),
        
        BrokerSite(
            name="PeekYou",
            url="https://www.peekyou.com", 
            opt_out_url="https://www.peekyou.com/about/contact/optout/",
            form_fields={
                "email": "email",
                "first_name": "first_name",
                "last_name": "last_name"
            },
            instructions="Profile removal request",
            difficulty="medium",
            requires_verification=True
        ),
        
        BrokerSite(
            name="Radaris",
            url="https://radaris.com",
            opt_out_url="https://radaris.com/page/how-to-remove",
            form_fields={
                "email": "email"
            },
            instructions="Find your profile first, then request removal",
            difficulty="medium",
            requires_verification=True
        ),
        
        BrokerSite(
            name="SearchPeopleFree",
            url="https://www.searchpeoplefree.com",
            opt_out_url="https://www.searchpeoplefree.com/removal",
            form_fields={
                "email": "email"
            },
            instructions="Locate your profile and request removal",
            difficulty="medium", 
            requires_verification=True
        ),
        
        BrokerSite(
            name="ThatsThem",
            url="https://thatsthem.com",
            opt_out_url="https://thatsthem.com/optout", 
            form_fields={
                "email": "email"
            },
            instructions="Email-based removal process",
            difficulty="easy",
            requires_verification=True
        ),
        
        BrokerSite(
            name="VoterRecords",
            url="https://voterrecords.com",
            opt_out_url="https://voterrecords.com/faq", 
            form_fields={
                "email": "email"
            },
            instructions="Contact via FAQ page for removal",
            difficulty="hard",
            requires_verification=True
        ),
        
        # International/specialized brokers
        BrokerSite(
            name="192.com",
            url="https://www.192.com", 
            opt_out_url="https://www.192.com/atoz/opt-out/",
            form_fields={
                "email": "email",
                "first_name": "firstName",
                "last_name": "lastName"
            },
            instructions="UK-based directory service",
            difficulty="medium",
            requires_verification=True
        )
    ]