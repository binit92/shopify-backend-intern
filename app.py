from flask import Flask, render_template, url_for, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
from io import StringIO

# __name
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


#decorator
@app.route('/', methods=['POST', 'GET'])
def index():
    #print("index")
    if request.method == 'POST':
        inv_content = request.form['content']
        new_inv = Inventory(content = inv_content)

        try:
            db.session.add(new_inv)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding inventory'
        
    else:
        all_inventory = Inventory.query.order_by(Inventory.date_created).all()

        return render_template('index.html', all_inventory = all_inventory)


@app.route('/delete/<int:id>')
def delete(id):
    #print("delete", id)
    inv_to_delete = Inventory.query.get_or_404(id)

    try:
        db.session.delete(inv_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that inventory'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    #print("update", id)
    inv = Inventory.query.get_or_404(id)

    if request.method == 'POST':
        inv.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue updating your inventory"
    else:
        return render_template('update.html', inv=inv)

@app.route('/export', methods=['GET', 'POST'])
def export():
    #print("export method ")
    si = StringIO()
    cw = csv.writer(si)
    all_inventory = Inventory.query.order_by(Inventory.date_created).all()
    print(all_inventory)
    cw.writerow(["id", "content", "date"])
    for inv in all_inventory:
        inv_list = [ str(inv.id), inv.content, str(inv.date_created)]
        cw.writerow(inv_list)
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=report.csv'
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == "__main__":
    app.run(debug=True)