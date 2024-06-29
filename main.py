import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

class RequestHandler(BaseHTTPRequestHandler):

    def load_data(self, filename):
        with open(filename, 'r') as file:
            return json.load(file)

    def save_data(self, filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file)

    def render_template(self, template, context={}):
        with open(template, 'r') as file:
            html = file.read()
            for key, value in context.items():
                html = html.replace('{{ ' + key + ' }}', str(value))
        return html

    def do_GET(self):
        if self.path in ['/', '/home']:
            furniture = self.load_data('data/furniture.json')
            content = self.render_template('templates/index.html', {'furniture': furniture})
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/register':
            content = self.render_template('templates/register.html')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/login':
            content = self.render_template('templates/login.html')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path == '/account':
            content = self.render_template('templates/profile.html')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/furniture/'):
            furniture_id = int(self.path.split('/')[-1])
            furniture = self.load_data('data/furniture.json')
            item = next((f for f in furniture if f['id'] == furniture_id), None)
            content = self.render_template('templates/furniture.html', {'item': item})
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/search'):
            query = parse_qs(self.path.split('?')[1])['query'][0]
            furniture = self.load_data('data/furniture.json')
            results = [f for f in furniture if query.lower() in f['name'].lower() or query.lower() in f['description'].lower()]
            content = self.render_template('templates/search.html', {'furniture': results})
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/booking/'):
            furniture_id = int(self.path.split('/')[-1])
            furniture = self.load_data('data/furniture.json')
            item = next((f for f in furniture if f['id'] == furniture_id), None)
            content = self.render_template('templates/booking.html', {'item': item})
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/payment/'):
            booking_id = int(self.path.split('/')[-1])
            content = self.render_template('templates/payment.html', {'booking_id': booking_id})
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = parse_qs(self.rfile.read(content_length).decode('utf-8'))

        if self.path == '/register':
            users = self.load_data('data/users.json')
            new_user = {
                'id': len(users) + 1,
                'username': post_data['username'][0],
                'email': post_data['email'][0],
                'password': post_data['password'][0]
            }
            users.append(new_user)
            self.save_data('data/users.json', users)
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()

        elif self.path == '/login':
            users = self.load_data('data/users.json')
            email = post_data['email'][0]
            password = post_data['password'][0]
            user = next((u for u in users if u['email'] == email and u['password'] == password), None)
            if user:
                self.send_response(302)
                self.send_header('Location', '/home')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()

        elif self.path == '/account':
            users = self.load_data('data/users.json')
            user_id = int(post_data['user_id'][0])
            user = next((u for u in users if u['id'] == user_id), None)
            if user:
                user['username'] = post_data['username'][0]
                user['email'] = post_data['email'][0]
                self.save_data('data/users.json', users)
                self.send_response(302)
                self.send_header('Location', '/account')
                self.end_headers()

        elif self.path.startswith('/booking/'):
            bookings = self.load_data('data/bookings.json')
            new_booking = {
                'id': len(bookings) + 1,
                'user_id': int(post_data['user_id'][0]),
                'furniture_id': int(post_data['furniture_id'][0]),
                'start_date': post_data['start_date'][0],
                'end_date': post_data['end_date'][0]
            }
            bookings.append(new_booking)
            self.save_data('data/bookings.json', bookings)
            self.send_response(302)
            self.send_header('Location', '/home')
            self.end_headers()

        elif self.path.startswith('/payment/'):
            payments = self.load_data('data/payments.json')
            new_payment = {
                'id': len(payments) + 1,
                'booking_id': int(post_data['booking_id'][0]),
                'amount': float(post_data['amount'][0]),
                'payment_method': post_data['payment_method'][0]
            }
            payments.append(new_payment)
            self.save_data('data/payments.json', payments)
            self.send_response(302)
            self.send_header('Location', '/home')
            self.end_headers()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
