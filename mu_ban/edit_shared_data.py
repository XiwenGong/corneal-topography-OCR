import pickle
import os

PKL_PATH = os.path.join(os.path.dirname(__file__), 'shared_data.pkl')

def load_data():
    if not os.path.exists(PKL_PATH):
        return {}
    with open(PKL_PATH, 'rb') as f:
        return pickle.load(f)

def save_data(data):
    with open(PKL_PATH, 'wb') as f:
        pickle.dump(data, f)

def print_menu():
    print("\n==== shared_data.pkl 编辑工具 ====")
    print("1. 查看所有键值对")
    print("2. 增加/修改键值对")
    print("3. 删除键")
    print("4. 保存并退出")
    print("5. 退出不保存")

def main():
    data = load_data()
    while True:
        print_menu()
        choice = input("请选择操作: ").strip()
        if choice == '1':
            if not data:
                print("(空)")
            else:
                for k, v in data.items():
                    print(f"{k}: {v}")
        elif choice == '2':
            key = input("输入要增加/修改的键: ").strip()
            value = input("输入该键的新值(字符串): ")
            data[key] = value
            print(f"已设置 {key}: {value}")
        elif choice == '3':
            key = input("输入要删除的键: ").strip()
            if key in data:
                del data[key]
                print(f"已删除 {key}")
            else:
                print("该键不存在")
        elif choice == '4':
            save_data(data)
            print("已保存并退出")
            break
        elif choice == '5':
            print("未保存，直接退出")
            break
        else:
            print("无效选择，请重试")

if __name__ == '__main__':
    main() 