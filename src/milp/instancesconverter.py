import os

def prepare_data(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    num_couriers = int(lines[0].strip())
    num_packages = int(lines[1].strip())
    capacities = list(map(int, lines[2].split()))
    sizes = list(map(int, lines[3].split()))
    distances = [list(map(int, line.split())) for line in lines[4:]]

    with open(output_file, 'w') as f:
        f.write(f"set COURIERS := {' '.join(map(str, range(1, num_couriers+1)))};\n")
        f.write(f"set PACKAGES := {' '.join(map(str, range(1, num_packages+1)))};\n\n")

        f.write("param capacity :=\n")
        for i, cap in enumerate(capacities, 1):
            f.write(f"{i} {cap}\n")
        f.write(";\n\n")

        f.write("param size :=\n")
        for i, s in enumerate(sizes, 1):
            f.write(f"{i} {s}\n")
        f.write(";\n\n")

        f.write("param distance :\n")
        f.write("    " + " ".join(map(str, range(1, num_packages+2))) + " :=\n")
        for i, row in enumerate(distances):
            f.write(f"{i+1} " + " ".join(map(str, row)) + "\n")
        f.write(";\n")

def process_directory(input_dir, output_dir):
    # Create output directory if it doesn't exist
    #if not os.path.exists(output_dir):
        #os.makedirs(output_dir)
    
    # Process each file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".dat"):  # Assuming input files are .txt
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"converted_{filename}")
            prepare_data(input_path, output_path)
            print(f"Processed {filename} -> converted_{filename}")

def main():
    try:
        input_dir = 'src/instances'
        output_dir = 'src/milp/data'
        process_directory(input_dir, output_dir)
    except:
        print('Something goes wrong')
        
if __name__ == '__main__':
    main()
