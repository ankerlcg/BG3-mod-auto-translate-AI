
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices.ComTypes;
using System.Text;
using System.Threading.Tasks;
using LSLib.LS;
using LSLib.LS.Enums;

namespace BG3Pack
{
    public class PackageManage
    {
        public static void UnPackageFile(string packagePath,string unpackageDir)
        {
            LSLib.LS.Packager pkg = new LSLib.LS.Packager();
            pkg.UncompressPackage(packagePath, unpackageDir);
        }


        public static void CreatePackage(string dataDir,string outPath)
        {
            var options = new PackageCreationOptions();
            options.Version = PackageVersion.V18;
            options.Compression = CompressionMethod.LZ4;
            options.FastCompression = false;
            options.Flags |= PackageFlags.Solid;
            options.Flags |= PackageFlags.AllowMemoryMapping;
            options.Flags |= PackageFlags.Preload;
            decimal a = 0;
            options.Priority = (byte)a;
            var packager = new Packager();
            packager.CreatePackage(outPath, dataDir, options);

        }

    }
}
