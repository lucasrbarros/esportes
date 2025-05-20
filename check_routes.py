from app import app

def list_routes():
    print("Rotas disponíveis na aplicação:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:50s} {rule.methods} {rule.rule}")

if __name__ == "__main__":
    list_routes() 