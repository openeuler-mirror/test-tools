#include <httplib.h>
#include <iostream>
#include <string>

int main() {
    httplib::Server svr;
    svr.Get("/", [](const httplib::Request& req, httplib::Response& res) {
        res.set_content("Welcome to OS Dark Web Interface", "text/plain");
    });
    svr.listen("0.0.0.0", 8080);
    return 0;
} 