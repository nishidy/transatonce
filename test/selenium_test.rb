require "selenium-webdriver"
require "rspec"

describe "transatonceのテスト" do

    before(:all) do 
        @hostname = "transatonce.appspot.com"

        @data = ["driver", "学習", "at once"]

        @driver = Selenium::WebDriver.for :firefox
        @driver.navigate.to "http://"+@hostname
      
        @driver.find_element(:xpath, "//form/input[contains(@value,'Clear')]").click

        textbox = @driver.find_element(:xpath, "//form/textarea")
        textbox.send_keys(@data.join("\n"))
      
        @driver.find_element(:xpath, "//form/input[contains(@value,'Trans')]").click

        wait = Selenium::WebDriver::Wait.new(:timeout => 15)
        begin
            wait.until { @driver.find_element(:id, "disp_2") }
        rescue
        end

    end

    it "翻訳した単語が表示される" do
        @driver.navigate.to "http://"+@hostname
        textbox = @driver.find_element(:xpath, "//form/textarea")
        #puts textbox.methods
        expect(textbox.attribute("value")).to eq @data.join("\n")
    end

    it "追加した単語が表示される" do
        newdata = ["newly"]

        @driver.navigate.to "http://"+@hostname
        textbox = @driver.find_element(:xpath, "//form/textarea")
        textbox.clear()
        textbox.send_keys(newdata.join(""))
        @driver.find_element(:xpath, "//form/input[contains(@value,'Trans')]").click

        @driver.navigate.to "http://"+@hostname
        textbox = @driver.find_element(:xpath, "//form/textarea")
        expect(textbox.attribute("value")).to eq (@data+newdata).join("\n")
    end

    it "重複した単語は表示されない" do
        newdata = ["newly","redundant"]

        @driver.navigate.to "http://"+@hostname
        textbox = @driver.find_element(:xpath, "//form/textarea")
        textbox.clear()
        textbox.send_keys((@data+newdata).join("\n"))
      
        @driver.find_element(:xpath, "//form/input[contains(@value,'Trans')]").click

        wait = Selenium::WebDriver::Wait.new(:timeout => 15)
        begin
            wait.until { @driver.find_element(:id, "disp_3") }
        rescue
        end

        @driver.navigate.to "http://"+@hostname
        textbox = @driver.find_element(:xpath, "//form/textarea")

        @data << newdata
        expect(textbox.attribute("value")).to eq (@data).join("\n")
    end

    it "重複した単語を翻訳した後, 追加した単語が表示される" do
        newdata = ["repeatedly"]

        @driver.navigate.to "http://"+@hostname
        textbox = @driver.find_element(:xpath, "//form/textarea")
        textbox.clear()
        textbox.send_keys(newdata.join(""))
        @driver.find_element(:xpath, "//form/input[contains(@value,'Trans')]").click

        @driver.navigate.to "http://"+@hostname
        textbox = @driver.find_element(:xpath, "//form/textarea")
        expect(textbox.attribute("value")).to eq (@data+newdata).join("\n")
    end

    after(:all) do
        @driver.find_element(:xpath, "//form/input[contains(@value,'Clear')]").click
        @driver.quit
    end

end

