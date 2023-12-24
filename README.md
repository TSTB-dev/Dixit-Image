# Dixit-Image

Dixit-ImageはDixitを開発する上で必要となる実装のsubsetです．画像生成やキャプション生成などの機能を揃えています．

## Getting Started

Dixit-Imageを利用するには，以下の手順に従ってください．:

1. Clone the repository:
   ```
   git clone https://github.com/TSTB-dev/Dixit-Image.git
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run streamlit by:
    ```
    streamlit run main.py
    ```

## AIプレイヤーによる投票
プレイヤーが場に出した4枚の画像から，AIプレイヤーは親のタイトルと最も類似する画像を選択します．現状の実装では，GPT4-VもしくはGemini Pro Visionを用いて類似度のスコアを予測しています．実装のサンプルは以下のコマンドを実行すると，起動します．
   ```
   streamlit run ai_vote_sample.py
   ```
このサンプルでは，`./images`ディレクトリを参照して，その内部の画像から4枚の画像を選択し，適当な親のタイトルの設定とGPT4Vによるその解析を行えます．

## 親のテキストからの画像生成(DALL・E3)
Comming soon...





## Contributing

We welcome contributions from the community! If you have an idea or improvement, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature.
3. Make your changes.
4. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Thanks to all the contributors who have helped to build Dixit-Image.
- Special thanks to the open-source community for their continuous support.

## Contact

For any queries or suggestions, feel free to open an issue or contact the maintainers directly.

Happy coding!

---

Dixit-Image Team

---

Please adjust the content according to the specific details and goals of your project.