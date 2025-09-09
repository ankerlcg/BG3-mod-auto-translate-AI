using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using BG3Pack;



namespace test
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            BG3Pack.PackageManage.unPackageFile("C:\\Users\\ankerlcg\\PycharmProjects\\Bg3Mod\\test\\test.pak", "C:\\Users\\ankerlcg\\PycharmProjects\\Bg3Mod\\mod-unpak\\");
            //BG3Pack.PackageManage.createPackage("C:\\Users\\ankerlcg\\PycharmProjects\\Bg3Mod\\mod-unpak\\act1_capes_139ee212-9e2c-78ef-7pgb", "C:\\Users\\ankerlcg\\PycharmProjects\\Bg3Mod\\mod-unpak\\act1_capes_139ee212-9e2c-78ef-7pgb\\1.pak");
        }
    }
}
