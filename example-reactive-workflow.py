# Copyright 2018 Ghent University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.





#
#  SSL certificate layer
#

@when_all(
    'config.set.domain-name',
    'packages.installed')
@when_not(
    'certificate.registered',
    'certificate.requests-stop')
def register_certificate():
    # ... (register ssl certificate)
    set_flag('certificate.registered')


@when_all(
    '20-days-later',
    'certificate.registered')
def signal_renew_required():
    # ... (stop web app)
    clear_flag('20-days-later')
    set_flag('certificate.renew.required')
    # This should be unset by an upper layer after a stop
    set_flag('certificate.requests-stop')


@when_all(
    'certificate.registered',
    'certificate.renew.required')
@when_not('certificate.requests-stop')
def renew_certificate():
    # ... (renew certificate)
    clear_flag('certificate.renew.required')


@when_all(
    'certificate.registered',
    'config.changed.domain-name',
)
def signal_new_certificate():
    remove_flag('certificate.registered')
    set_flag('certificate.requests-stop')



#
#  Webserver layer
#

@when_not('packages.installed')
def install_packages():
    # ... (install packages)
    set_flag('packages.installed')


@when_all(
    'packages.installed',
    'packages.upgrade-available')
def upgrade_packages():
    # ... (upgrade packages)
    clear_flag('packages.upgrade-available')
    set_flag('packages.changed')



#
#  Webapp layer
#

@when('packages.installed')
@when_not('webapp.deployed')
def deploy_web_app():
    # ... (deploy web app)
    set_flag('wepapp.deployed')


@when_all(
    'webapp.deployed',
    'certificate.registered')
@when_not(
    'webapp.started',
    'certificate.renew-required')
def start_web_app():
    # ... (start web app)
    set_flag('certificate.started')


@when_all('certificate.requests-stop')
@when('webapp.started')
def stop_web_app():
    # ... (stop web app)
    clear_flag('certificate.requests-stop')
    clear_flag('webapp.started')


trigger(when='packages.changed', set='webapp.packaged.changed')


@when(
    'webapp.started',
    'webapp.packages.changed')
def reload_webapp():
    # ... (reload webapp)
    clear_flag('packages.changed')
    clear_flag('webapp.packages.changed')
