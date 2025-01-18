from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)
from IPython.display import HTML, display
from dbt.cli.main import dbtRunner, dbtRunnerResult
import pandas as pd
from copydf import copyDF


@magics_class
class DBTMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.dbt = dbtRunner()
        # dbt show --limit は指定がなければ、デフォルト5になるので指定する
        self.limit = 50  # デフォルトのリミット
        self.quiet = True  # quiet オプション（デフォルト）
    
    # 変換した SQL を表示する関数（折りたたみ対応）
    def display_converted_sql(self, sql):
        html_content = f"""
        <details>
            <summary>Converted SQL (Click to expand)</summary>
            <pre>{sql}</pre>
        </details>
        """
        display(HTML(html_content))
    
    def _run_dbt_command(self, cli_args):
        if self.quiet:
            cli_args.append("--quiet")
            
        res: dbtRunnerResult = self.dbt.invoke(cli_args)
        if not res.success:
            raise RuntimeError(f"dbt command execution failed: {res.exception}")
        if not res.result:
            print("Execution result is empty")
            return None
        return res

    @line_magic
    def config(self, line):
        key, value = line.split('=')
        key = key.strip()
        value = value.strip()
        if key == 'dbt.limit':
            self.limit = int(value)
        elif key == 'dbt.quiet':
            self.quiet = value.lower() == 'true'

    @cell_magic
    def dbt_show(self, line, cell):
        cli_args = ["show", "--inline", cell, "--limit", str(self.limit)]

        res = self._run_dbt_command(cli_args)
        df = pd.DataFrame([row.dict() for r in res.result for row in r.agate_table])

        # line.strip() をチェックして適切な処理を実行
        if line.strip() == 'copydf':
            # データフレームをクリップボードにコピー
            # Dcoker環境でも使えるようにcopyDFを使用
            copyDF(df)
            display(f"DataFrame copied to clipboard.")
            display(df)
            display(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

        elif line.strip().isidentifier():  # 変数名として有効か確認

            self.shell.user_ns[line.strip()] = df
            display(f"Results stored in variable '{line.strip()}'.")

        else:
            # 変数名でも 'copydf' でもない場合は、データフレームをそのまま表示
            display(df)
            display(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    @cell_magic
    def dbt_compile(self, line, cell):
        cli_args = ["compile", "--inline", cell]
        
        res = self._run_dbt_command(cli_args)
        compiled_sql = res.result[0].node.compiled_code
        self.display_converted_sql(compiled_sql)

    # @cell_magic
    # def dbt_debug(self, line, cell):
    #     cli_args = ["debug"]
    #     res: dbtRunnerResult = self.dbt.invoke(cli_args)