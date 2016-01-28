/**
 *  fetch to download count of zhitou app, which need to login by user abd password.
 */

//var casper = require('casper').create();
var casper = require('casper').create({
    pageSettings: {
        userAgent: 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'
    }
});
var platform = casper.cli.get(0);

if (platform == 'appchina'){

    casper.start('http://dev.appchina.com/market/dev/index.action', function(){});

    casper.waitForSelector('form#loginForm', function(){
        this.sendKeys('input#inputEmail', '18516255432');
        this.sendKeys('input#inputPassword', 'Chinasc0pe1');
        this.click('input[type="submit"]');
    }, null, 30000);

    casper.waitForSelector('div[class="apps widget-content"]', function(){
        var appText = this.evaluate(function(){
            return $('div[class="apps widget-content"] span').text();
        });
        if (/.*?(\d+).*?(\d+).*?(\d+).*?/g.test(appText)){
            return this.echo(RegExp.$2  + RegExp.$3);
        }
        return this.echo(0);
    }, null, 30000);

    casper.run();

} else if (platform == 'app_mi') {

    casper.start('http://dev.xiaomi.com/home?userId=543824783', function(){});

    casper.waitForSelector('form#miniLogin', function(){
        this.sendKeys('input#miniLogin_username', 'developer@chinascopefinancial.com');
        this.sendKeys('input#miniLogin_pwd', 'abc_123_');
        this.click('input#message_LOGIN_IMMEDIATELY');
    }, null, 60000);

    casper.waitForSelector('div.main', function(){
        this.thenOpen('http://dev.xiaomi.com/datacenter/appview/2882303761517263225?userId=543824783');
    }, null, 30000);

    casper.waitForSelector('table.table.table-bordered', function(){
        var appText = this.evaluate(function(){
            return $('table.table.table-bordered tr').eq(1).find('td').eq(0).text();
        });

        return this.echo(appText.replace(/,|\s/g, ''));
    }, null, 30000);

    casper.run();

} else if (platform == 'jifeng') {

    casper.start('http://dev.gfan.com/Aspx/DevApp/LoginUser.aspx', function(){});

    casper.waitForSelector('table#login_form', function(){
        this.sendKeys('input#loginUser_txtEmail', 'chinascope');
        this.sendKeys('input#loginUser_txtPsw', 'Chinasc0pe1');
        this.click('input#loginUser_btnSubmit');
    }, null, 30000);

    casper.waitForSelector('table[class="t_1202"]', function(){
        var appText = this.evaluate(function(){
            return $('table[class="t_1202"] tr').eq(1).find('td').eq(5).text();
        });

        return this.echo(appText.replace(/,|\s/g, ''));
    }, null, 30000);

    casper.run();

}
