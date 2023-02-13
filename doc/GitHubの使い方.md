# GitHubの使い方

## 機能追加の流れ
### 1. issueを作成
わかりやすいように書きましょう。特にルールはないです。
![](images/issue.png)

### 2. ブランチの作成
ブランチを作成する前に以下のコマンドを打っておきましょう。mainブランチに最新の状態を反映させることができます。
```sh
git switch main
git pull
```


ブランチ名のルール ： issueを作成すると #8 のように issueそれぞれに番号が与えられます。
`8-(作成する機能名など)` というように名前を付けてください。
ブランチを作成するコマンドは以下の通りです。
```sh
git switch -c ブランチ名
```

<!-- VScodeを用いた方法 折り畳み表示 -->
<details>
<summary>VScodeを用いた方法</summary>
<img src="images/branch.png" width="500px">
<div>
VScodeの左下にあるブランチのアイコンをクリックすると、ブランチの選択画面が出てきます。
</div>
<img src="images/branch_main.png" width="500px">
<div>
まずはmainブランチに切り替えます。
</div>
<img src="images/pull.png" width="500px">
<div>
mainブランチに最新の状態を反映させます。
</div>
<img src="images/branch_create.png" width="500px">
<div>
ブランチを作成します。
</div>
<img src="images/branch_name.png" width="500px">
<div>
ブランチの名前は `(issue番号)-(作成する機能名など)` というように名前を付けてください。
</div>
</details>

### 3. コミットまでの流れ
作業が完了したら、まずは作業したファイルをaddします。
```sh
git add (ファイル名)
```
すべてのファイルをaddする場合は以下のコマンドを打ちましょう。
```sh
git add .
```

次にcommitします。
```sh
git commit -m "#8 (作成した機能の概要など)"
```
コミットメッセージにもissue番号を先頭につけてください。

最後にpushします。
```sh
git push origin ブランチ名
```

<!-- VScodeを用いた方法 折り畳み表示 -->
<details>
<summary>VScodeを用いた方法</summary>
<img src="images/git_icon.png" width="500px">
<div>
作業が完了したら、VScodeの左側にある Git のアイコンをクリックします。
</div>
<img src="images/git_add.png" width="500px">
<div>
作業したファイルを「＋」 ボタンを押すことによってaddします。
</div>
<img src="images/git_commit.png" width="500px">
<div>
ステージされていることを確認し、コミットメッセージを記入したら、青色のコミットボタンを押します。
</div>
</details>

作業したブランチにpushしたら、GitHubのページに移動します。

### 4. Pull Requestの作成
![](images/pull_request1.png)
GitHubのページに移動したら、上の方にある `Pull requests` をクリック、`New pull request` をクリックします。

![](images/pull_request2.png)
`base: main` になっていることを確認し、`compare: ブランチ名` をクリックします。